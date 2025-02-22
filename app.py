from shiny import App, ui, reactive, render
from shinywidgets import render_widget, output_widget
from pathlib import Path
import pandas as pd
import geopandas as gpd
import shapely.wkt
from ipyleaflet import Map, GeoData, basemaps

# ------------------------------------------------------------------------
# SOURCE LAYERS
# ------------------------------------------------------------------------

## Load data
R3_1_geo = pd.read_excel('MaptionnaireR3_results_2025-01-03.xlsx', sheet_name='Click on map to draw polygon an')
R3_2_geo = pd.read_excel('MaptionnaireR3_results_2025-02-10.xlsx', sheet_name='Click on map to draw polygon an')

## Concatenate datasets
geo_full = pd.concat([R3_1_geo, R3_2_geo])

## Load study area boundary
SA_bndry = gpd.read_file("shps/SA_bndry/All Study Area Boundaries.shp").to_crs("EPSG:4326")

## Convert DataFrame to GeoDataFrame
geo_full = geo_full.dropna(subset=['WKT'])  
geo_full['geometry'] = geo_full['WKT'].apply(shapely.wkt.loads)
geo_full_gdf = gpd.GeoDataFrame(geo_full, geometry='geometry', crs="EPSG:4326")


## Clean for display
geo_full_gdf['time'] = geo_full_gdf['First Active Time'].astype(str)
geo_full_gdf['comment'] = geo_full_gdf['Add place-specific comment below:']
geo_full_gdf = geo_full_gdf[['time', 'comment', 'geometry']]



# ------------------------------------------------------------------------
# DEFINE UI
# ------------------------------------------------------------------------

app_ui = ui.page_fillable(
    ui.page_navbar(
        ui.nav_panel(
            "Maptionnaire R3 Results",
            ui.row(
                ui.h4("R3 comments"),
                ui.output_data_frame("comments_table"),
        ),
            ui.row(
                "comments here",
                output_widget("map")  
            ),
        ),
        title=ui.img(src='img/Utile U - Brown.png', style="max-width:12px;width:100%"),
        gap = 300,
        window_title="Maptionnaire R3 comments",
    )
)

# ------------------------------------------------------------------------
# SERVER LOGIC
# ------------------------------------------------------------------------

def server(input, output, session):
    @render.data_frame
    def comments_table():
        return render.DataGrid(
            geo_full_gdf[['time', 'comment']],
            width='100%',
            height='250px',  
            selection_mode="row",
            styles=[
                {"cols": [0], "style": {"width": "150px", "minWidth": "150px", "maxWidth": "200px"}},  # 'time' column
                {"cols": [1], "style": {"width": "500px", "minWidth": "400px", "maxWidth": "600px"}},  # 'comment' column
            ]
        )
    
    @render_widget
    def map():
        m = Map(center=(33.7582, -84.4229), zoom=11, scroll_wheel_zoom=True,
                basemap=basemaps.CartoDB.Positron, attribution_control=False, layout={'height': '500px'})
        
        selected = geo_full_gdf.iloc[list(comments_table.cell_selection()["rows"])]

        # Study Area Layer
        SA_lyr = GeoData(
            geo_dataframe=SA_bndry,
            style={'color': 'black', 'fillColor': 'transparent', 'opacity': 1, 'weight': 0.5, 'fillOpacity': 0.6},
            hover_style={'fillColor': 'transparent', 'fillOpacity': 0.2},
            name='Study Area Boundaries'
        )
        m.add(SA_lyr)

        # Round 3 Comments Layer
        R3_lyr = GeoData(
            geo_dataframe=geo_full_gdf,
            style={'color': 'black', 'fillColor': 'red', 'opacity': 0.05, 'weight': 1.9, 'dashArray': '2', 'fillOpacity': 0.1},
            hover_style={'fillColor': 'white', 'fillOpacity': 0.2},
            name='Round 3 Comments'
        )
        m.add(R3_lyr)

        selected_lyr = GeoData(
        geo_dataframe= selected,
        style={'color': 'yellow', 'fillColor': 'transparent', 'opacity': 1, 'weight': 2, 'fillOpacity': 1},  
        hover_style={'fillColor': 'transparent', 'fillOpacity': 0.2},  # Use style_callback for dynamic updates
        name='Selected'
        )
        m.add(selected_lyr)

        return m


# ------------------------------------------------------------------------
# RUN APP
# ------------------------------------------------------------------------

static_dir = Path(__file__).parent / "static"
app = App(app_ui, server, static_assets=static_dir)


