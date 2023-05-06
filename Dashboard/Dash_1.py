# activate MDA_env
# cd C:\Users\Gebruiker\Documents\DataScience\MDA\Project MDA\
# python Dash_1.py


import pandas as pd
import plotly.express as px
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import seaborn as sns
from statsmodels.nonparametric.smoothers_lowess import lowess
from Locations import combined_df, noise_df


# Create a Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Page 1", href="#", className="nav-link")),
        dbc.NavItem(dcc.Link("Page 2", href="#", className="nav-link")),
    ],
    brand="Leuven Noise Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)

# Map
map_fig = px.scatter_mapbox(
    combined_df,
    lat="latitude",
    lon="longitude",
    hover_name="name",
    hover_data=["type"],
    color="type",
    zoom=12,
    mapbox_style="carto-positron",
)


# Noise metric buttons
noise_metric_buttons = dbc.Row(
    [
        dbc.Label("Select noise metric", className="mb-2"),
        dbc.RadioItems(
            id="noise_metric",
            options=[
                {"label": "Lamax", "value": "lamax"},
                {"label": "Laeq", "value": "laeq"},
                {"label": "Lceq", "value": "lceq"},
                {"label": "Lcpeak", "value": "lcpeak"},
            ],
            value="laeq",
            inline=True,
        ),
    ],
    
)

# weather metric buttons
weather_metric_buttons = dbc.Row(
    [
        dbc.Label("Select weather metric", className="mb-2"),
        dbc.RadioItems(
            id="weather_metric",
            options=[
                {"label": "Temperature", "value": "LC_TEMP"},
                {"label": "Humidity", "value": "LC_HUMIDITY"},
                {"label": "Rain intensity", "value": "LC_RAININ"},
            ],
            value="LC_TEMP",
            inline=True,
        ),
    ],
)




# Month and Day bar selections
month_bar = dcc.Slider(
    id="month_slider",
    min=1,
    max=12,
    step=1,
    value=1,
    marks={m: f"Month {m}" for m in range(1, 13)},
)
day_bar = dcc.Slider(
    id="day_slider",
    min=1,
    max=31,
    step=1,
    value=1,
    marks={d: f"Day {d}" for d in range(1, 32)},
)





def update_line_chart(metric, month, day, location):
    filtered_data = noise_df[(noise_df["Month"] == month) & (noise_df["Day"] == day) & (noise_df["name"] == location)]
    
    # Use lowess from statsmodels with custom frac and it parameters
    lowess_line = lowess(filtered_data[metric], filtered_data["Hour"], frac=0.3, it=3)
    
    # Create scatter plot and add lowess line
    updated_scatter_chart = px.scatter(filtered_data, x="Hour", y=metric)
    updated_scatter_chart.add_scatter(x=lowess_line[:, 0], y=lowess_line[:, 1], mode="lines", line=dict(color="red"), name="Trend")
    
    return updated_scatter_chart


location = noise_df["name"]

# App layout
app.layout = html.Div(
    children=[
        navbar,
        dbc.Container(
            [
                dbc.Row(html.H1("Select a location on the map to get output")),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3("Map"),
                                dcc.Graph(id="map", figure=map_fig, clickData=None),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                html.H3("Location Information"),
                                html.Div(id="location_info"),
                            ],
                            md=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3(id="line_chart_title", children="Line Chart for Noise Data"),
                                noise_metric_buttons,
                                html.H4("Select Month"),
                                month_bar,
                                html.H4("Select Day"),
                                day_bar,
                                dcc.Graph(id="line_chart"),
                            ],
                            md=6,
                        ),
                        dbc.Col(
                            [
                                html.H3(id="weather_chart_title", children="Line Chart for Weather Data"),
                                weather_metric_buttons,
                                dcc.Graph(id="weather_chart"),
                            ],
                            md=6,
                        ),
                    ]
                ),
            ],
            fluid=True,
        ),
    ]
)


@app.callback(
    Output("line_chart_location", "children"),
    [Input("map", "clickData")],
)
def update_location(clickData):
    if clickData:
        idx = clickData["points"][0]["pointIndex"]
        location = combined_df.iloc[idx]["name"]
        return location
    return ""

@app.callback(
    Output("location_info", "children"),
    [Input("map", "clickData")],
)
def update_location_info(clickData):
    return display_map_info(clickData)

@app.callback(
    Output("line_chart", "figure"),
    [
        Input("noise_metric", "value"),
        Input("month_slider", "value"),
        Input("day_slider", "value"),
        Input("map", "clickData"),
    ],
)
def update_line_chart_based_on_location(metric, month, day, clickData):
    if clickData:
        idx = clickData["points"][0]["pointIndex"]
        location = combined_df.iloc[idx]["name"]
        correct_location = noise_df[noise_df["name"] == location]["name"].values[0]
        updated_scatter_chart = update_line_chart(metric, month, day, correct_location)
        
        return updated_scatter_chart
    else:
        return px.scatter()


def update_line_chart_based_on_location(metric, month, day, clickData):
    if clickData:
        idx = clickData["points"][0]["pointIndex"]
        location = combined_df.iloc[idx]["name"]
        correct_location = noise_df[noise_df["name"] == location]["name"].values[0]
        updated_scatter_chart = update_line_chart(metric, month, day, correct_location)
        
        return updated_scatter_chart
    else:
        return px.scatter()

@app.callback(
    Output("weather_chart", "figure"),
    [
        Input("weather_metric", "value"),
        Input("month_slider", "value"),
        Input("day_slider", "value"),
        Input("map", "clickData"),
    ],
)

def update_weather_chart_based_on_location(metric, month, day, clickData):
    if clickData:
        idx = clickData["points"][0]["pointIndex"]
        location = combined_df.iloc[idx]["name"]
        correct_location = noise_df[noise_df["name"] == location]["name"].values[0]
        weather_data = noise_df[(noise_df["Month"] == month) & (noise_df["Day"] == day) & (noise_df["name"] == correct_location)]
        weather_chart = px.line(weather_data, x="Hour", y=metric, title="Weather Data")
        
        return weather_chart
    else:
        return px.line()




def display_map_info(clickData):
    if clickData:
        idx = clickData["points"][0]["pointIndex"]
        row = combined_df.iloc[idx]
        return html.Table(
            [
                html.Tr([html.Th("name"), html.Td(row["name"])]),
                html.Tr([html.Th("Lamax"), html.Td(row["lamax"])]),
                html.Tr([html.Th("Laeq"), html.Td(row["laeq"])]),
                html.Tr([html.Th("Lceq"), html.Td(row["lceq"])]),
                html.Tr([html.Th("Lcpeak"), html.Td(row["lcpeak"])]),
                html.Tr([html.Th("Humidity"), html.Td(row["LC_HUMIDITY"])]),
                html.Tr([html.Th("Dew Point Temperature"), html.Td(row["LC_DWPTEMP"])]),
                html.Tr([html.Th("Number of events"), html.Td(row["number_of_events"])])
            ]
        )
    return "Click on a point to see more information."









if __name__ == "__main__":
    app.run_server(debug=True)
