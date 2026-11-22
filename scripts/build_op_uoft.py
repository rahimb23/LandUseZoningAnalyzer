#!/usr/bin/env python3
"""Rebuild data/op_uoft.json from the U of T Map & Data Library land use layer.

Source: "Toronto Land Use Spatial Data - parcel-level - (2019-2021)",
University of Toronto Map & Data Library, CC BY-NC 4.0, doi:10.5683/SP3/1VMJAG.
It is an unofficial reconstruction of the City's 2019 Official Plan land use
maps (Maps 13 to 23) on November 2021 property boundaries, and is not updated.

Usage:
    pip install pyshp shapely pyproj
    python3 scripts/build_op_uoft.py
"""
import io
import json
import pathlib
import urllib.request
import zipfile

import shapefile
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform

FILE_URL = "https://borealisdata.ca/api/access/datafile/315976"  # LanduseParcelsMergedv0120220106.zip
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "op_uoft.json"
MIN_AREA_M2 = 50       # drop slivers
SIMPLIFY_M = 1.5       # simplification tolerance in metres (UTM 17N)


def main():
    raw = urllib.request.urlopen(FILE_URL, timeout=300).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    stem = next(n[:-4] for n in z.namelist() if n.endswith(".shp"))
    reader = shapefile.Reader(shp=io.BytesIO(z.read(stem + ".shp")),
                              shx=io.BytesIO(z.read(stem + ".shx")),
                              dbf=io.BytesIO(z.read(stem + ".dbf")))
    to_wgs84 = Transformer.from_crs(26917, 4326, always_xy=True).transform

    def ring(coords):
        return [[round(x, 5), round(y, 5)] for x, y in coords]

    features = []
    for sr in reader.iterShapeRecords():
        cls = sr.record["Class_name"]
        if not cls:
            continue
        geom = shape(sr.shape.__geo_interface__)
        if not geom.is_valid:
            geom = geom.buffer(0)
        for part in getattr(geom, "geoms", [geom]):
            if part.area < MIN_AREA_M2:
                continue
            simple = part.simplify(SIMPLIFY_M, preserve_topology=True)
            if simple.is_empty:
                continue
            w = transform(to_wgs84, simple)
            features.append({
                "type": "Feature",
                "properties": {"lu": cls},
                "geometry": {"type": "Polygon",
                             "coordinates": [ring(w.exterior.coords)] + [ring(r.coords) for r in w.interiors]},
            })
    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")))
    print(f"{len(features)} polygons -> {OUT}")


if __name__ == "__main__":
    main()
