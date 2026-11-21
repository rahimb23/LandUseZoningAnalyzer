#!/usr/bin/env python3
"""Rebuild data/zoning.json and data/context.json from City of Toronto open GIS services.

Usage:  python3 scripts/fetch_data.py
Needs only the Python standard library.
"""
import json
import pathlib
import urllib.parse
import urllib.request

OUT = pathlib.Path(__file__).resolve().parent.parent / "data"

ZONING = "https://services3.arcgis.com/b9WvedVPoizGfvfD/arcgis/rest/services/COTGEO_ZBL_ZONE/FeatureServer/0/query"
MAJOR_ROADS = "https://gis.toronto.ca/arcgis/rest/services/cot_geospatial/MapServer/3/query"
SHORELINE = "https://gis.toronto.ca/arcgis/rest/services/cot_geospatial/MapServer/14/query"
SUBWAY = "https://gis.toronto.ca/arcgis/rest/services/cot_geospatial7/MapServer/11/query"


def query(url, out_fields, offset=0, count=2000, simplify=0.00003):
    params = {
        "where": "1=1", "outFields": out_fields, "outSR": 4326, "geometryPrecision": 5,
        "maxAllowableOffset": simplify, "resultOffset": offset, "resultRecordCount": count,
        "orderByFields": "OBJECTID", "f": "geojson",
    }
    with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(params), timeout=120) as r:
        return json.load(r)["features"]


def query_all(url, out_fields, simplify):
    feats, offset = [], 0
    while True:
        page = query(url, out_fields, offset, simplify=simplify)
        feats += [f for f in page if f.get("geometry")]
        if len(page) < 2000:
            return feats
        offset += 2000


def main():
    OUT.mkdir(exist_ok=True)
    zones = query_all(ZONING, "ZN_ZONE,ZN_STRING", 0.00003)
    zoning = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"z": f["properties"]["ZN_ZONE"], "s": f["properties"]["ZN_STRING"]},
         "geometry": f["geometry"]} for f in zones]}
    (OUT / "zoning.json").write_text(json.dumps(zoning, separators=(",", ":")))
    print(f"zoning: {len(zones)} polygons")

    roads = query_all(MAJOR_ROADS, "LINEAR_NAME_FULL", 0.00005)
    shore = query_all(SHORELINE, "OBJECTID", 0.00005)
    subway = query_all(SUBWAY, "ROUTE_LONG_NAME,ROUTE_COLOR", 0.00005)
    ctx = {
        "roads": [{"type": "Feature", "properties": {"n": f["properties"]["LINEAR_NAME_FULL"]}, "geometry": f["geometry"]} for f in roads],
        "subway": [{"type": "Feature", "properties": {"n": f["properties"]["ROUTE_LONG_NAME"], "c": "#" + f["properties"]["ROUTE_COLOR"]},
                    "geometry": f["geometry"]} for f in subway],
        "shore": [{"type": "Feature", "properties": {}, "geometry": f["geometry"]} for f in shore],
    }
    (OUT / "context.json").write_text(json.dumps(ctx, separators=(",", ":")))
    print(f"context: {len(roads)} road segments, {len(subway)} rapid transit lines, {len(shore)} shoreline segments")


if __name__ == "__main__":
    main()
