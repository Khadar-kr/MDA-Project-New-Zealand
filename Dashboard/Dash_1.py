# activate MDA_env
# cd C:\Users\Gebruiker\Documents\DataScience\MDA\Project MDA\
# python Dash_1.py

import pandas as pd
import plotly.express as px
import dash
import numpy as np

from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import seaborn as sns
from statsmodels.nonparametric.smoothers_lowess import lowess
from Locations import combined_df


color_events = {
    "Human voice - Shouting": "#636EFA",
    "Human voice - Singing": "#EF553B",
    "Music non-amplified": "#00CC96",
    "Nature elements - Wind": "#AB63FA",
    "Transport road - Passenger car": "#FFA15A",
    "Transport road - Siren": "#19D3F3",
}

event_columns = ["Human voice - Shouting", "Human voice - Singing", "Music non-amplified",
                 "Nature elements - Wind", "Transport road - Passenger car", "Transport road - Siren"]

month_dict = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep',
              10: 'Oct', 11: 'Nov', 12: 'Dec'}

# Create a Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Event Page", href="/events", className="nav-link")),
        dbc.NavItem(dcc.Link("Detailed Page", href="/detailed", className="nav-link")),
    ],
    brand="Leuven Noise Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)





# Get unique location names
locations_events = combined_df["name"].unique().tolist()
locations_events.append("All locations")

# Define layout for dropdown
dropdown_layout = html.Div([
    dcc.Dropdown(
        id='location-dropdown',
        options=[{'label': i, 'value': i} for i in locations_events],
        value='All locations',
        clearable=False
    )
])



def interpret_trend(y_values, month_dict, threshold=0.5):
    # Get the differences between consecutive values to find where the trend changes
    changes = np.diff(y_values)
    
    trends = []
    trend_start = 0
    is_increasing = changes[0] > 0

    # Determine the steepness of the initial trend
    if abs(changes[0]) > threshold:
        steepness = "sharp"
    else:
        steepness = "gradual"

    # Record high and low points
    high_points = []
    low_points = []

    for i in range(1, len(changes)):
        current_increase = changes[i] > 0
        if is_increasing != current_increase or i == len(changes) - 1:
            trend_end = i if i != len(changes) - 1 else i + 1
            trend_word = 'increase' if is_increasing else 'decrease'
            trends.append(f'a {steepness} {trend_word} from {month_dict[trend_start+1]} to {month_dict[trend_end+1]}')
            trend_start = trend_end
            is_increasing = current_increase

            # If the trend changes, record a high/low point
            if is_increasing:
                low_points.append(month_dict[trend_end+1])
            else:
                high_points.append(month_dict[trend_end+1])

            # Determine the steepness of the new trend
            if abs(changes[i]) > threshold:
                steepness = "sharp"
            else:
                steepness = "gradual"

    trend_descriptions = ', '.join(trends)
    high_points_str = ', '.join(high_points)
    low_points_str = ', '.join(low_points)

    if high_points:
        trend_descriptions += f'. The high points were in {high_points_str}.'
    if low_points:
        trend_descriptions += f' The low points were in {low_points_str}.'

    return trend_descriptions


@app.callback(
    Output('pie-chart', 'figure'),
    [Input('location-dropdown', 'value')]
)
def update_pie_chart(location):
    if location == 'All locations':
        event_sums = combined_df[event_columns].sum()
    else:
        event_sums = combined_df[combined_df['name'] == location][event_columns].sum()  

    pie_plot = go.Figure(data=[go.Pie(labels=event_sums.index, values=event_sums.values)])
    pie_plot.update_traces(marker=dict(colors=[color_events[key] for key in event_sums.index]))
    pie_plot.update_layout(title="Event Types")

    return pie_plot


@app.callback(
    Output('bar-chart', 'figure'),
    Output('category-dropdown', 'options'),
    Output('interpretation-text', 'children'),
    Output('trend-summary-table', 'children'),
    Input('location-dropdown', 'value'),
    Input('category-dropdown', 'value'),
)
def update_bar_chart_and_insights(location, selected_category):
    # The code from update_bar_chart() starts here
    if location == 'All locations':
        df_grouped = combined_df.melt(id_vars=['Month'], value_vars=event_columns, var_name='Event Type',
                                      value_name='Count').groupby(['Month', 'Event Type']).sum().reset_index()
    else:
        df_grouped = combined_df[combined_df['name'] == location].melt(id_vars=['Month'], value_vars=event_columns,
                                                                       var_name='Event Type',
                                                                       value_name='Count').groupby(
            ['Month', 'Event Type']).sum().reset_index()

    df_pivot = df_grouped.pivot(index='Month', columns='Event Type', values='Count').fillna(0)
    df_pivot.index = df_pivot.index.map(month_dict)
    category_options = [{'label': col, 'value': col} for col in df_pivot.columns]

    bar_chart_events = go.Figure(
        data=[
            go.Bar(
                x=df_pivot.index,
                y=df_pivot[col],
                name=col,
                marker_color=color_events[col],
            )
            for col in df_pivot.columns
        ]
    )

    bar_chart_events.update_layout(barmode='stack')

    trend_summary_table = []
    interpretation_text = ''
    
    if selected_category:
        x_values = np.array(list(range(1, len(df_pivot.index) + 1)))
        y_values = df_pivot[selected_category]
        lowess_smoothed = lowess(y_values, x_values, frac=0.4)
        trend_summary = interpret_trend(lowess_smoothed[:, 1], month_dict)

        x_values_month_names = [month_dict[val] for val in x_values]
        bar_chart_events.add_trace(
            go.Scatter(x=x_values_month_names, y=lowess_smoothed[:, 1], mode='lines',
                       name=f'Trend line for {selected_category}'))


    # The code from update_insights() starts here
    if location == "All locations":
        event_sums = combined_df[event_columns].sum()
    else:
        event_sums = combined_df[combined_df["name"] == location][event_columns].sum()

    total_events = event_sums.sum()
    top_events = event_sums.nlargest(3).index.tolist()

    interpretation_text = f"In {location}, a total of {int(total_events)} events occurred. "
    interpretation_text += f"The top three events were {', '.join(top_events)}."

    if selected_category:
        if trend_summary:
            interpretation_text += f" Examining the {selected_category} category, we noticed that the trend has {trend_summary}."
            # Add a check for trend_summary before creating the table
            
        else:
            interpretation_text += f" Examining the {selected_category} category, but no trend was discernable."
    else:
        interpretation_text += f" Select a category to see trends."

    return bar_chart_events, category_options, interpretation_text, trend_summary_table



# Define layouts for elements on the event page
event_counts_layout = html.Div(id='event-counts')

insights_layout = html.Div([
    html.H4("Insights"),
    html.Div(id='interpretation-text'),
    html.Div(id='trend-summary-table'),
])




# Define the layout for the event page
event_page = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                    html.Div(
                            id="event_totals",
                            children=[
                            html.H4("Events per Category"),
                                dropdown_layout,
                                event_counts_layout,
                            dcc.Dropdown(
                                id='category-dropdown',
                                options=[],
                                value=None,
                                placeholder='Select a category',
                                clearable=False
                                ),
                            insights_layout
                            ],
                        ),
                    ],
                    md=6,
                    style={"padding-top": "20px"},
                ),
                dbc.Col(
                    [
                        html.H3("Event Types"),
                        dcc.Graph(id='pie-chart'),
                    ],
                    md=6,
                    style={"padding-top": "20px"},
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(id='bar-chart'),
                        html.Div(id='trend-summary')  
                    ]
                )
            ]
        ),
        dcc.Store(id='store')
    ],
    fluid=True,
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
    filtered_data = combined_df[(combined_df["Month"] == month) & (combined_df["Day"] == day) & (combined_df["name"] == location)]
    
    # Use lowess from statsmodels with custom frac and it parameters
    lowess_line = lowess(filtered_data[metric], filtered_data["Hour"], frac=0.3, it=3)
    
    # Create scatter plot and add lowess line
    updated_scatter_chart = px.scatter(filtered_data, x="Hour", y=metric)
    updated_scatter_chart.add_scatter(x=lowess_line[:, 0], y=lowess_line[:, 1], mode="lines", line=dict(color="red"), name="Trend")
    
    # Add reference lines
    reference_lines = {
        50: "Light traffic",
        60: "Conversational speech",
        70: "Shower",
        75: "Vacuum cleaner",
    }

    colors = ["green", "purple", "orange", "cyan"]

    for (value, label), color in zip(reference_lines.items(), colors):
        updated_scatter_chart.add_trace(
            go.Scatter(
                x=[0, filtered_data["Hour"].max()],
                y=[value, value],
                mode="lines",
                line=dict(color=color, dash="dash"),
                name=label,
                legendgroup=label,
                hoverinfo="skip"
            )
        )

    return updated_scatter_chart




location = combined_df["name"]

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/events':
        return event_page
    elif pathname == '/detailed':
        return detailed_page
    else:
        return html.Div([
            html.H3('No page at this address: go to /events or /detailed'),
        ])

@app.callback(
    Output("line_chart_location", "children"),
    [Input("map", "clickData")],
)
def update_location(clickData, month, day):
    if clickData:
        location = clickData["points"][0]["hovertext"]
        filtered_data = combined_df[(combined_df["Month"] == month) & (combined_df["Day"] == day) & (combined_df["name"] == location)].iloc[0]
        return location
    return ""

@app.callback(
    Output("location_info", "children"),
    [
        Input("map", "clickData"),
        Input("month_slider", "value"),
        Input("day_slider", "value"),
    ],
)
def update_location_info(clickData, month, day):
    return display_map_info(clickData, month, day)

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
        location = clickData["points"][0]["hovertext"]
        updated_scatter_chart = update_line_chart(metric, month, day, location)
        
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
        location = clickData["points"][0]["hovertext"]
        weather_data = combined_df[(combined_df["Month"] == month) & (combined_df["Day"] == day) & (combined_df["name"] == location)]
        weather_chart = px.line(weather_data, x="Hour", y=metric, title="Weather Data")
        
        return weather_chart
    else:
        return px.line()


def display_map_info(clickData, month, day):
    if clickData:
        location = clickData["points"][0]["hovertext"]
        filtered_data = combined_df[(combined_df["Month"] == month) & (combined_df["Day"] == day) & (combined_df["name"] == location)]

        if filtered_data.empty:
            return "No data available. Please select a different location or a different time point."

        filtered_data = filtered_data.iloc[0]
        
        # Retrieve the day name from the filtered_data DataFrame
        day_name = filtered_data['day_name']

        return html.Table(
            [
                html.Tr([html.Th("Date"), html.Td(f"{day_name}, {month}/{day}")]),
                html.Tr([html.Th("Lamax"), html.Td(round(filtered_data["lamax"], 2))]),
                html.Tr([html.Th("Laeq"), html.Td(round(filtered_data["laeq"], 2))]),
                html.Tr([html.Th("Lceq"), html.Td(round(filtered_data["lceq"], 2))]),
                html.Tr([html.Th("Lcpeak"), html.Td(round(filtered_data["lcpeak"], 2))]),
                html.Tr([html.Th("Humidity"), html.Td(round(filtered_data["LC_HUMIDITY"], 2))]),
                html.Tr([html.Th("Dew Point Temperature"), html.Td(round(filtered_data["LC_DWPTEMP"], 2))])                
            ]
        )
    return "Click on a point to see more information."

def plot_occupancy(df, location, day_name):
    # Filter the DataFrame for the given location and day
    df_location_day = df[(df['name'] == location) & df['popularTimesHistogram'].notnull() & (df['day_name'] == day_name)]
    # Extract the data for the given day
    day_data = df_location_day['popularTimesHistogram']
    # Extract the hours and occupancy percentages
    hours = []
    occupancy = []
    for data in day_data:
        day_data = data[day_name]
        hours.extend([item['hour'] for item in day_data])
        occupancy.extend([item['occupancyPercent'] for item in day_data])
    # Create a bar chart for this day
    occupancy_plot = go.Figure(
        data=[
            go.Bar(
                x=hours,
                y=occupancy
            )
        ],
        layout=go.Layout(
            title=f'Occupancy for {location} on {day_name}',
            xaxis=dict(title="Hour"),
            yaxis=dict(title="Occupancy Percent"),
        ),
    )
    return occupancy_plot
@app.callback(
    Output("occupancy_plot", "figure"),
    [
        Input("map", "clickData"),
        Input("day_slider", "value"),
    ],
)
def update_occupancy_plot(clickData, day_slider_value):
    if clickData:
        location = clickData["points"][0]["hovertext"]
        # Filter the DataFrame for the given location and day of the month
        df_location_day = combined_df[(combined_df['name'] == location) & (combined_df['Day'] == day_slider_value)]
        # Check if we have data for this location and day
        if df_location_day.empty:
            return px.bar()
        else:
            # Get the name of the day from the 'day_name' column
            day_name = df_location_day['day_name'].iloc[0]
            return plot_occupancy(df_location_day, location, day_name)
    # If we don't have clickData or there is no data for the location, return an empty plot
    return px.bar()

@app.callback(
    Output("location_header", "children"),
    [Input("map", "clickData")],
)
def update_location_header(clickData):
    if clickData:
        location = clickData["points"][0]["hovertext"]
        return f"Location Information for {location}"
    return "Location Information"


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])


detailed_page = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Select a point on the map to see more information"),
                        dcc.Graph(id="map", figure=map_fig, clickData=None),
                        html.H4("Select a month you want to see"),
                        month_bar,
                        html.H4("Select day you want to see"),
                        day_bar,
                        html.H3(id="location_header", children="Location Information"),
                        html.Div(id="location_info"),
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        
                        html.H3(id="line_chart_title", children="Line Chart for Noise Data"),
                        noise_metric_buttons,
                        
                        dcc.Graph(id="line_chart"),
                        html.H3(id="weather_chart_title", children="Line Chart for Weather Data"),
                        weather_metric_buttons,
                        dcc.Graph(id="weather_chart"),
                        html.H3("Occupancy Information"),
                        dcc.Graph(id="occupancy_plot"),
                    ],
                    md=6,
                ),
            ]
        ),
    ],
    fluid=True,
)

if __name__ == "__main__":
    app.run_server(debug=True)