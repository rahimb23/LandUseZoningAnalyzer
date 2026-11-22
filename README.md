# Land Use Compatibility Analysis

A browser tool for screening land use compatibility around a site in the City of Toronto. Place a site on the map, set a study radius, and the tool clips every land use polygon to that circle. It then reports what surrounds the site and how compatible those uses are with the site.

It has two separate maps, because zoning and the Official Plan often disagree:

- **Zoning:** City of Toronto Zoning By-law 569-2013, from City of Toronto Open Data.
- **Official Plan:** land use designations from the University of Toronto Map & Data Library (see the disclaimer below). You can replace this layer with your own file.

The site panel shows the zone and the OP designation side by side and flags a mismatch.

> **Disclaimer: the Official Plan layer is unofficial and out of date.** The City does not publish its OP land use designations as open data. The bundled layer is the U of T Map & Data Library's *Toronto Land Use Spatial Data, parcel-level (2019–2021)*. It reconstructs the City's 2019 land use maps (Maps 13 to 23) on November 2021 property boundaries, using image classification. It does not include Official Plan amendments made since 2019, may misclassify some parcels, and has no Utility Corridors class. Always confirm designations against the City's current [Official Plan maps](https://www.toronto.ca/city-government/planning-development/official-plan-guidelines/official-plan/official-plan-maps-copy/). The tool shows this warning whenever the U of T layer is on screen.

## Features

- Click anywhere to place a site, or jump to an example site.
- Open the tool on a specific site from a link: `?site=43.672,-79.466&r=300` (latitude, longitude, radius in metres).
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

## Using your own Official Plan layer

If you have a current copy of the OP land use designations, for example from City Planning, switch to the Official Plan map and choose **Load your own file**. The tool accepts:

- a zipped Shapefile (`.zip` containing `.shp`, `.dbf` and `.prj`), or
- a GeoJSON file.

Coordinates in WGS84, NAD83 MTM zone 10 (EPSG:2952 / 2019) or UTM zone 17N are detected and reprojected. The tool picks the attribute field whose values best match the designation names, such as Neighbourhoods, Apartment Neighbourhoods, Mixed Use Areas and Core Employment Areas, whatever the spacing or capitals. You can change the field in the panel. Values that don't match a known designation are grouped as "Other / unmatched" and are not rated.

Your file replaces the U of T layer and is stored only in your browser (IndexedDB), so it is still there the next time you open the page. It is never uploaded. **Go back to U of T data** removes it.

## Compatibility ratings

Every category maps to one of ten land use families. A symmetric matrix in `index.html` (`PAIRS`) rates each pair of families. It reflects Official Plan policy themes: transition in scale between Neighbourhoods and taller forms, protection of employment areas, and keeping sensitive uses away from heavy industry (MECP D-6). The matrix is a simplified screening aid, not a policy determination. Adjust it to suit your practice.

## Data

| File | Source | Notes |
| --- | --- | --- |
| `data/zoning.json` | [COTGEO_ZBL_ZONE](https://services3.arcgis.com/b9WvedVPoizGfvfD/arcgis/rest/services/COTGEO_ZBL_ZONE/FeatureServer) | 11,892 zone polygons, simplified. Lands still under former municipal by-laws are not in this layer. |
| `data/op_uoft.json` | [Toronto Land Use Spatial Data, parcel-level (2019–2021)](https://doi.org/10.5683/SP3/1VMJAG), University of Toronto Map & Data Library | 21,732 polygons, simplified to 1.5 m. **CC BY-NC 4.0: non-commercial use only, with attribution.** Unofficial; see the disclaimer above. |
| `data/context.json` | City of Toronto GIS (`gis.toronto.ca`): major centreline, shoreline, TTC rapid transit routes | Drawn for orientation only. |

The zoning and context files come from City of Toronto Open Data under the Open Government Licence – Toronto. To refresh them, run:

```bash
python3 scripts/fetch_data.py
```

To rebuild the Official Plan file from the U of T download, run:

```bash
pip install pyshp shapely pyproj
python3 scripts/build_op_uoft.py
```

## Libraries

Leaflet 1.9.4, Turf 6.5.0, proj4js 2.9.0 and shpjs 4.0.4, all loaded from CDNs.
