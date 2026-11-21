# Land Use Zoning Analyzer

A browser tool for screening land use compatibility around a site in the City of Toronto. Place a site on the map, set a study radius, and the tool clips every land use polygon to that circle. It then reports what surrounds the site and how compatible those uses are with the site.

It has two separate maps, because zoning and the Official Plan often disagree:

- **Zoning:** City of Toronto Zoning By-law 569-2013. This layer ships with the repo.
- **Official Plan:** land use designations (Maps 13 to 23). You load this layer from your own file (see below).

When both layers are loaded, the site panel shows the zone and the OP designation side by side and flags a mismatch.

## Features

- Click anywhere to place a site, or jump to an example site.
- Radius from 50 to 1,500 m, with presets for 120 m (Planning Act notice), 400 m (5-minute walk) and 800 m (MTSA / 10-minute walk).
- Area in hectares and share of the radius for each land use category. Streets, rail and water are reported separately because they carry no designation.
- A compatibility screen that rates each surrounding use as Compatible, Transition or Conflict. It rates against the use at the site, or against a proposed use you choose.
- The nearest potential conflict and its approximate distance and direction.
- A direction compass showing the dominant use on each side of the site, split into the near and far half of the radius.
- A "Copy summary" button that produces plain text for a planning report.

## Run it

The page loads its data with `fetch`, so serve it over HTTP. Opening `index.html` straight from disk won't work.

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000. The page also works on GitHub Pages: enable Pages for the `main` branch, root folder.

## Loading the Official Plan layer

The City does not publish the OP land use designations as open data or as a public web service. If you have the layer, switch to the Official Plan map and drop in one of these:

- a zipped Shapefile (`.zip` containing `.shp`, `.dbf` and `.prj`), or
- a GeoJSON file.

Coordinates in WGS84, NAD83 MTM zone 10 (EPSG:2952 / 2019) or UTM zone 17N are detected and reprojected. The tool picks the attribute field whose values best match the designation names, such as Neighbourhoods, Apartment Neighbourhoods, Mixed Use Areas and Core Employment Areas. You can change the field in the panel. Values that don't match any known designation are grouped as "Other / unmatched" and are not rated.

The file is stored only in your browser (IndexedDB), so it is still there the next time you open the page. It is never uploaded.

## Compatibility ratings

Every category maps to one of ten land use families. A symmetric matrix in `index.html` (`PAIRS`) rates each pair of families. It reflects Official Plan policy themes: transition in scale between Neighbourhoods and taller forms, protection of employment areas, and keeping sensitive uses away from heavy industry (MECP D-6). The matrix is a simplified screening aid, not a policy determination. Adjust it to suit your practice.

## Data

| File | Source | Notes |
| --- | --- | --- |
| `data/zoning.json` | [COTGEO_ZBL_ZONE](https://services3.arcgis.com/b9WvedVPoizGfvfD/arcgis/rest/services/COTGEO_ZBL_ZONE/FeatureServer) | 11,892 zone polygons, simplified. Lands still under former municipal by-laws are not in this layer. |
| `data/context.json` | City of Toronto GIS (`gis.toronto.ca`): major centreline, shoreline, TTC rapid transit routes | Drawn for orientation only. |

All of these come from City of Toronto Open Data under the Open Government Licence – Toronto. To refresh them, run:

```bash
python3 scripts/fetch_data.py
```

## Libraries

Leaflet 1.9.4, Turf 6.5.0, proj4js 2.9.0 and shpjs 4.0.4, all loaded from CDNs.
