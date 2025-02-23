import pandas as pd
import geopandas as gpd
import shapely.wkt

## Load data
R3_1_geo = pd.read_excel('MaptionnaireR3_results_2025-01-03.xlsx', sheet_name='Click on map to draw polygon an')
R3_2_geo = pd.read_excel('MaptionnaireR3_results_2025-02-10.xlsx', sheet_name='Click on map to draw polygon an')

## Concatenate datasets
geo_full = pd.concat([R3_1_geo, R3_2_geo])

## Load study area boundary
SA_bndry = gpd.read_file("shps/SA_bndry/All Study Area Boundaries.shp").to_crs("EPSG:4326")
SA_bndry = SA_bndry.drop(columns=['CREATED_US', 'CREATED_DA', 'LAST_EDITE', 'LAST_EDI_1'])
SA_bndry.to_file("sa.geojson", driver="GeoJSON")

## Convert DataFrame to GeoDataFrame
geo_full = geo_full.dropna(subset=['WKT'])  
geo_full['geometry'] = geo_full['WKT'].apply(shapely.wkt.loads)
geo_full_gdf = gpd.GeoDataFrame(geo_full, geometry='geometry', crs="EPSG:4326")


## Clean for display
geo_full_gdf['time'] = geo_full_gdf['First Active Time'].astype(str)
geo_full_gdf['comment'] = geo_full_gdf['Add place-specific comment below:']
geo_full_gdf = geo_full_gdf[['time', 'comment', 'geometry']]
geo_full_gdf.to_file("comments.geojson", driver="GeoJSON")
