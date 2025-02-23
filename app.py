from shiny import App, ui, reactive, render
from shinywidgets import render_widget, output_widget
from pathlib import Path
import geopandas as gpd
from ipyleaflet import Map, GeoData, basemaps
from traitlets import observe

# ------------------------------------------------------------------------
# SOURCE DATA
# ------------------------------------------------------------------------

study_areas = gpd.read_file("sa.geojson")
comments = gpd.read_file("comments.geojson")
comments["time"] = comments["time"].astype(str)

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
            ui.row("comments here", output_widget("map")),
        ),
        title=ui.img(src="img/Utile U - Brown.png", style="max-width:12px;width:100%"),
        gap=300,
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
            comments[["time", "comment"]],
            width="100%",
            height="250px",
            selection_mode="row",
            styles=[
                {
                    "cols": [0],
                    "style": {
                        "width": "150px",
                        "minWidth": "150px",
                        "maxWidth": "200px",
                    },
                },  # 'time' column
                {
                    "cols": [1],
                    "style": {
                        "width": "500px",
                        "minWidth": "400px",
                        "maxWidth": "600px",
                    },
                },  # 'comment' column
            ],
        )

    @reactive.effect
    def f():
        selected_rows = list(comments_table.cell_selection()["rows"])
        filtered_df = comments.iloc[selected_rows]
        selected_lyr = GeoData(
            geo_dataframe=filtered_df,
            style={
                "color": "yellow",
                "fillColor": "transparent",
                "opacity": 1,
                "fillOpacity": 1,
                "weight": 2,
            },
            name="Selected",
        )
        map.widget.add(selected_lyr)

    @render_widget
    def map():

        m = Map(
            center=(33.7582, -84.4229),
            zoom=11,
            scroll_wheel_zoom=True,
            basemap=basemaps.CartoDB.Positron,
            attribution_control=False,
            layout={"height": "500px"},
        )

        # Study Area Layer
        SA_lyr = GeoData(
            geo_dataframe=study_areas,
            style={
                "color": "black",
                "fillColor": "transparent",
                "opacity": 1,
                "weight": 0.5,
                "fillOpacity": 0.6,
            },
            name="Study Area Boundaries",
        )

        # Round 3 Comments Layer
        R3_lyr = GeoData(
            geo_dataframe=comments,
            style={
                "color": "black",
                "opacity": 0.05,
                "fillColor": "red",
                "fillOpacity": 0.1,
                "weight": 1.9,
                "dashArray": "2",
            },
            name="Round 3 Comments",
        )

        m.add(SA_lyr)
        m.add(R3_lyr)

        return m


# ------------------------------------------------------------------------
# RUN APP
# ------------------------------------------------------------------------

static_dir = Path(__file__).parent / "static"
app = App(app_ui, server, static_assets=static_dir)
