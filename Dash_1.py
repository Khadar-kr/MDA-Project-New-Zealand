# Activate MDA_env
# cd C:\Users\Gebruiker\Documents\DataScience\MDA\Project MDA\
# python Dash_1.py

import pandas as pd
import plotly.express as px
import dash
import numpy as np

from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess
from Locations import combined_df,events_data_df,predicted

# Define colors for event types
color_events = {
    "Human Voice - Shouting": "#636EFA",
    "Human Voice - Singing": "#EF553B",
    "Music non-amplified": "#00CC96",
    "Natural elements - Wind": "#AB63FA",
    "Transport road- Passenger car": "#FFA15A",
    "Transport road - Siren": "#19D3F3",
}

event_columns = ['Human Voice - Shouting',
                'Human Voice - Singing',
                'Music non-amplified',
                'Natural elements - Wind',
                'Transport road- Passenger car',
                'Transport road - Siren'
]

event_columns_2 = ['Human voice - Shouting',
                'Human voice - Singing',
                'Music non-amplified',
                'Nature elements - Wind',
                'Transport road - Passenger car',
                'Transport road - Siren'
]

month_dict = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

# Create a Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/styles.css'])


# Elements for the sidebar
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "18.3rem",
    "padding": "2rem 1rem",
    "background-color": "#2a2d3e",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "position": "absolute",
    "top": 0,
    "left": "18rem", 
    "right": 0,
    "bottom": 0,
    "padding": "2rem 1rem",
    "overflow": "scroll"  
}

sidebar = html.Div(
    [
        html.H3("Leuven Noise Dashboard", className="display-5",style={"color": "white"}), 
        html.Hr(),   
        dbc.Nav(
            [
                dbc.NavLink("Home Page", href="/home", id="home-page-link",style={"color": "white"}),
                dbc.NavLink("Event Page", href="/events", id="event-page-link",style={"color": "white"}),
                dbc.NavLink("Detailed Page", href="/detailed", id="detailed-page-link",style={"color": "white"})
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)


######################
#      Home Page    #
#####################

# Creating variables for the home page
unique_names = combined_df['name'].unique()
location_count = len(unique_names)
mean_noise = round(combined_df['laeq'].mean())
max_noise_location = combined_df.groupby('name')['laeq'].mean().idxmax()
event_count = round(combined_df[event_columns_2].sum().sum())
# calculate the top 3 loudest event
loud_events_data = []  
# Iterate over each row in the original DataFrame
for i, row in combined_df.iterrows():
    for event in event_columns_2:
        if row[event] == 1:
            loud_events_data.append({'Event': event, 'laeq': row['laeq']})

loud_events_df = pd.DataFrame(loud_events_data)

# Find the top 3 event types with the highest mean 'laeq' noise levels
mean_noise_levels = loud_events_df.groupby('Event')['laeq'].mean()  
top_3_events = mean_noise_levels.nlargest(3)  

# Find the top 3 most frequent events 
event_frequencies = round(combined_df[event_columns_2].sum())
top_3_most_frequent_events = event_frequencies.nlargest(3)


# Calculate the percentage of noise levels above each reference line
total_samples = len(combined_df)

noise_ranges = {
    "below_50": (None, 50),
    "50_to_60": (50, 60),
    "60_to_70": (60, 70),
    "70_to_75": (70, 75),
    "75_to_80": (75, 80),
    "above_80": (80, None),
}
reference_descriptions = {
    "below_50": "lower than 50 db",
    "50_to_60": "between 50 db and 60 db (comparable to light traffic)",
    "60_to_70": "between 60 db and 70 db (comparable to conversational speech)",
    "70_to_75": "between 70 db and 75 db (comparable to a shower)",
    "75_to_80": "between 75 db and 80 db (comparable to a vacuum cleaner running)",
    "above_80": "above 80 db (sounds at this level can cause hearing damage)",
}
range_percents = {}
for range_name, (lower, upper) in noise_ranges.items():
    if lower is None:
        count_in_range = len(combined_df[combined_df['laeq'] < upper])
    elif upper is None:
        count_in_range = len(combined_df[combined_df['laeq'] > lower])
    else:
        count_in_range = len(combined_df[(combined_df['laeq'] > lower) & (combined_df['laeq'] <= upper)])
    percent = round((count_in_range / total_samples) * 100, 2)
    range_percents[range_name] = percent

# Calculate the percentage of noise levels and events during the day (7-22) and at night
day_start_hour = 7
day_end_hour = 22
day_noise_data = combined_df[(combined_df['Hour'] >= day_start_hour) & (combined_df['Hour'] <= day_end_hour)]
night_noise_data = combined_df[(combined_df['Hour'] < day_start_hour) | (combined_df['Hour'] > day_end_hour)]

day_noise_percent = round((day_noise_data['laeq'].count() / total_samples) * 100, 2)
night_noise_percent = round((night_noise_data['laeq'].count() / total_samples) * 100, 2)

day_event_percent = round((day_noise_data[event_columns_2].sum().sum() / event_count) * 100, 2)
night_event_percent = round((night_noise_data[event_columns_2].sum().sum() / event_count) * 100, 2)

mean_day_noise = round(day_noise_data['laeq'].mean())
mean_night_noise = round(night_noise_data['laeq'].mean())


# Calculating peak and low hours + values
average_noise_by_hour = combined_df.groupby('Hour')['laeq'].mean()
peak_hour = average_noise_by_hour.idxmax()
quiet_hour = average_noise_by_hour.idxmin()
peak_hour_noise_level = average_noise_by_hour.loc[peak_hour]
quiet_hour_noise_level = average_noise_by_hour.loc[quiet_hour]


# Extract night events 
night_events_data = []  
for i, row in night_noise_data.iterrows():
    for event in event_columns_2:
        if row[event] == 1:
            night_events_data.append({'Event': event, 'laeq': row['laeq']})

night_events_df = pd.DataFrame(night_events_data)
# Find the top 3 event types during night with the highest mean 'laeq' noise levels
mean_night_noise_levels = night_events_df.groupby('Event')['laeq'].mean()  
top_3_night_events = mean_night_noise_levels.nlargest(3)  

# Find the top 3 most frequent night events
night_event_frequencies = round(night_noise_data[event_columns_2].sum())
top_3_most_frequent_night_events = night_event_frequencies.nlargest(3)



# Update the home_page layout to include the distinction between day and night noise data
home_page = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Welcome to the Leuven Noise Dashboard!", style={"color": "white", "padding-left": "20px", "padding": "10px"}),
            html.H2(f"This tool offers an insightful glimpse into the noise patterns of Naamsestraat in Leuven.", style={"color": "white", "padding-left": "20px", "padding": "10px"}),

            html.Div([
                html.H3(
                    f"This dashboard provides insights into the noise patterns of Naamsestraat in Leuven.",
                    style={"color": "white", "padding-left": "20px", "padding": "10px"}
                ),
                html.P(
                    "You can explore the data collected from different locations, including hourly noise intensity data and events that occurred over the year 2022. Use the navigation menu to access other pages for more detailed information and visualizations.",
                    style={"color": "white", "padding-left": "20px", "padding": "10px"}
                ),
            ], style={"backgroundColor": "#2a2d3e"}),
            
            html.Div([
                html.P([
                    f"The overall mean noise level across Naamsestraat is {mean_noise} dB. {max_noise_location} stands out for having the highest mean noise level among the observed locations.",
                    html.Br(),
                    f"The loudest average noise levels were observed at {peak_hour}:00, reaching {peak_hour_noise_level:.2f} dB, while the quietest average noise levels were at {quiet_hour}:00, at {quiet_hour_noise_level:.2f} dB.",
                ], style={"color": "white", "padding-left": "20px", "padding": "10px"}),
            
                # information about the three loudest events
                html.P("In terms of loudness, these three events were the loudest:", style={"color": "white", "padding-left": "20px"}),
                *[html.P(f'{event}: {round(mean_noise_levels[event])} dB', style={"color": "white", "padding-left": "40px"}) for event in top_3_events.index],
                html.Hr(),

                # Information about the three most frequent events
                html.P("Shifting our focus to frequency, the three most common noise events recorded include:", style={"color": "white", "padding-left": "20px"}),
                *[html.P(f'{event}: {event_frequencies[event]} occurrences', style={"color": "white", "padding-left": "40px"}) for event in top_3_most_frequent_events.index],
            ], style={"backgroundColor": "#2a2d3e"}),

            # And information about the day and night noise data
            html.Hr(),
            html.Div([
                html.P([
                    "A survey from 2020 reveals that 45.1% of citizens living in the center of Leuven experience issues with noise at night.",
                    html.Br(),
                    f"The average noise level during the day was slightly higher at {mean_day_noise} dB compared to the quieter nighttime average of {mean_night_noise} dB.",
                    html.Br(),
                    f"Daytime events dominated the data, constituting {day_event_percent}% of all events, with nighttime events making up the remaining {night_event_percent}%.",
                ], style={"color": "white", "padding-left": "20px"}),
                # Add information about the top 3 night events
                html.Hr(),
                html.P("During the night, the three events where the loudest were:", style={"color": "white", "padding-left": "20px"}),
                *[html.P(f'{event}: {round(mean_night_noise_levels[event])} dB: {night_event_frequencies[event]} occurrences', style={"color": "white", "padding-left": "40px"}) for event in top_3_night_events.index],
            ], style={"backgroundColor": "#2a2d3e"})
        ], width=9),
        dbc.Col([
            html.Img(src="/assets/leuven_image.jpg", style={"width": "75%"}),
        ], width=3),
    ], style={"display": "flex"}),
], fluid=True, style=CONTENT_STYLE)

#link to survey: https://leuven.incijfers.be/jive : Stadsmonitor – samenleven – survey data – buurthinder – lawaai hinder 




######################
#     Event Page    #
#####################

# Get unique location names
locations_events = events_data_df["name"].unique().tolist()
locations_events.append("All locations")

# Define layout for dropdown
dropdown_layout = html.Div(
    [
        dcc.Dropdown(
            id="location-dropdown",
            options=[{"label": i, "value": i} for i in locations_events],
            value="All locations",
            clearable=False,
        )
    ]
)

def interpret_trend(y_values, month_dict):
    # Identify the indices of the max and min values
    sorted_indices = np.argsort(y_values)

    # Highest and second highest
    high_index = sorted_indices[-1]
    second_high_index = sorted_indices[-2]

    # Lowest and second lowest
    low_index = sorted_indices[0]
    second_low_index = sorted_indices[1]

    # Get the months corresponding to high and low points
    high_month = month_dict[high_index + 1]
    second_high_month = month_dict[second_high_index + 1]
    low_month = month_dict[low_index + 1]
    second_low_month = month_dict[second_low_index + 1]

    # Initialize description
    trend_description = ""

    # Check if high and low points are in the same month
    if high_index == low_index:
        trend_description = "remained fairly consistent with a high and low point in " + high_month
    else:
        # General trend direction
        if high_index < low_index:
            trend_description += f"Initially rose, reaching a peak in {high_month}, and then generally declined towards {low_month}. "
            if second_high_index > low_index and second_high_index < high_index:
                trend_description += f"The trend experienced another rise around {second_high_month}. "
            if second_low_index > high_index:
                trend_description += f"Finally, it fell once more towards a low in {second_low_month}."
        else:
            trend_description += f"Initially fell, hitting a low in {low_month}, and then generally climbed towards {high_month}. "
            if second_low_index > high_index and second_low_index < low_index:
                trend_description += f"The trend experienced another drop around {second_low_month}. "
            if second_high_index > low_index:
                trend_description += f"Finally, it rose again towards a peak in {second_high_month}."

    # Add final punctuation
    trend_description += "."

    return trend_description, high_month, low_month

@app.callback(
    Output("pie-chart", "figure"),
    [Input("location-dropdown", "value")],
)
def update_pie_chart(location):
    if location == "All locations":
        event_sums = events_data_df[event_columns].sum()
    else:
        event_sums = events_data_df[events_data_df["name"] == location][event_columns].sum()

    pie_plot = go.Figure(data=[go.Pie(labels=event_sums.index, values=event_sums.values)])
    pie_plot.update_traces(marker=dict(colors=[color_events[key] for key in event_sums.index]), textfont=dict(color="white"), insidetextfont=dict(color="white"), outsidetextfont=dict(color="white"))
    pie_plot.update_layout(
        title={
            'font': {
                'color': 'white',
                'family': 'Poppins, Regular'  
            }
        },
        plot_bgcolor='rgb(42,45,62)',
        paper_bgcolor='rgb(42,45,62)',
        legend={
            'font': {
                'color': 'white',
                'family': 'Poppins, Regular'  
            }
        },
        xaxis={'color': 'white'},
        yaxis={'color': 'white'}
    )

    return pie_plot


@app.callback(
    Output("bar-chart", "figure"),
    Output("category-dropdown", "options"),
    Output("interpretation-text", "children"),
    Output("trend-summary-table", "children"),
    Input("location-dropdown", "value"),
    Input("category-dropdown", "value"),
)
def update_bar_chart_and_insights(location, selected_category):
    if location == "All locations":
        df_grouped = events_data_df.melt(
            id_vars=["Month"],
            value_vars=event_columns,
            var_name="Event Type",
            value_name="Count",
        ).groupby(["Month", "Event Type"]).sum().reset_index()
    else:
        df_grouped = events_data_df[events_data_df["name"] == location].melt(
            id_vars=["Month"],
            value_vars=event_columns,
            var_name="Event Type",
            value_name="Count",
        ).groupby(["Month", "Event Type"]).sum().reset_index()

    df_pivot = df_grouped.pivot(index="Month", columns="Event Type", values="Count").fillna(0)

    # Sort index
    df_pivot.sort_index(inplace=True)

    df_pivot.index = df_pivot.index.map(month_dict)
    # Ensure all months are in the DataFrame
    df_pivot = df_pivot.reindex(list(month_dict.values()))

    # Fill NaNs with zero
    df_pivot.fillna(0, inplace=True)

    category_options = [{"label": col, "value": col} for col in df_pivot.columns]

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

    bar_chart_events.update_layout(barmode="stack")
    bar_chart_events.update_layout(
    title={
           'font': {
                'color': 'white',
                'family': 'Poppins, Regular'  
            }
    },
    plot_bgcolor='rgb(42,45,62)',
    paper_bgcolor='rgb(42,45,62)',
    legend={'font': {
                'color': 'white',
                'family': 'Poppins, Regular'  
            }},
    xaxis={'color': 'white'},
    yaxis={'color': 'white'}
    )


    trend_summary_table = []
    interpretation_text = ""

    if selected_category:
        x_values = np.array(list(range(1, len(df_pivot.index) + 1)))
        y_values = df_pivot[selected_category]
        lowess_smoothed = lowess(y_values, x_values, frac=0.4)
        trend_summary, high_points_str, low_points_str = interpret_trend(lowess_smoothed[:, 1], month_dict)

        x_values_month_names = [month_dict[val] for val in x_values]
        bar_chart_events.add_trace(
            go.Scatter(
                x=x_values_month_names,
                y=lowess_smoothed[:, 1],
                mode="lines",
                name=f"Trend line for {selected_category}",
            )
        )

    if location == "All locations":
        event_sums = events_data_df[event_columns].sum()
    else:
        event_sums = events_data_df[events_data_df["name"] == location][event_columns].sum()

    total_events = event_sums.sum()
    top_events = event_sums.nlargest(3).index.tolist()

    interpretation_text = [
        html.P(f"At {location}, a total of {int(total_events)} events occurred."),
        html.P("The top three events were:"),
        html.Ul([html.Li(event) for event in top_events]),
    ]   

    if selected_category:
        if trend_summary:
            interpretation_text.extend([
                html.P(f"Examining the {selected_category} category, we noticed that:"),
                html.Ul([html.Li(f"The trend has {trend_summary}")]),
            ])
            
            
            if high_points_str:
                interpretation_text.append(html.P(f"The {selected_category} was the highest in {high_points_str}."))
            if low_points_str:
                interpretation_text.append(html.P(f"The {selected_category} was the lowest in {low_points_str}."))
        else:
            interpretation_text.append(html.P(f"Examining the {selected_category} category, but no trend was discernible."))
    else:
        interpretation_text.append(html.P("Select a category to see trends."))



    return bar_chart_events, category_options, interpretation_text, trend_summary_table


# Define layouts for elements on the event page
event_counts_layout = html.Div(id="event-counts")

insights_layout = html.Div(
    [
        html.H4("Insights"),
        html.Div(id="interpretation-text", children='interpretation_text'),
        html.Div(id="trend-summary-table"),
    ]
)



# Define the layout for the event page
event_page = html.Div([
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                id="event_totals",
                                    children=[
                                        html.H4("Select a Location and an Event Category", className="mb-3", style={"color": "white"}),
                                        html.Div(dropdown_layout, style={"margin-bottom": "10px"}),  
                                            event_counts_layout,
                                            dcc.Dropdown(
                                                id="category-dropdown",
                                                options=[],
                                                value=None,
                                                placeholder="Select a category",
                                                clearable=False,
                                                className="mb-3",
                                                ),
                                        html.Div(insights_layout, style={"margin-top": "15px"}),
                                        ],
                                        className="card p-3 shadow",
                                        style={"backgroundColor": "#2a2d3e", "color": "white"},
                            ),
                        ],
                        md=6,
                        className="mb-4",
                    ),
                    dbc.Col(
                        [
                            html.H3("Total events over the year", className="mb-3", style={"color": "white"}),
                            dcc.Graph(id="pie-chart"),
                        ],
                        md=6,
                        className="card p-3 shadow",
                        style={"backgroundColor": "#2a2d3e"},
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Bar Chart", className="mb-3", style={"color": "white"}),
                            dcc.Graph(id="bar-chart"),
                            html.Div(id="trend-summary"),
                        ],
                        className="card p-3 shadow",
                        style={"backgroundColor": "#2a2d3e","margin-top": "7px"},
                    )
                ]
            ),
            dcc.Store(id="store"),
        ],
        fluid=True,
        className="p-4",
    ),
],style=CONTENT_STYLE)


######################
#    Detaild Page    #
#####################

# Create a default figure with the desired layout
default_fig = go.Figure()
default_fig.update_layout(
        plot_bgcolor='#2a2d3e',
        paper_bgcolor='#2a2d3e',
        legend={'font': {'color': 'white'}},
        xaxis={'color': 'white'},
        yaxis={'color': 'white'}
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
map_fig.update_layout(
    plot_bgcolor='#2a2d3e',
    paper_bgcolor='#2a2d3e',
    legend={'font': {
                'color': 'white',
                'family': 'Poppins, Regular'  
            }
        },
)

# weather metric buttons
weather_metric_buttons = dbc.Row(
    [
        dbc.Label("Select weather metric", className="mb-2", style={'color': 'white'}),
        dbc.RadioItems(
            id="weather_metric",
            options=[
                {"label": "Temperature", "value": "LC_TEMP"},
                {"label": "Rain intensity", "value": "LC_RAININ"},
            ],
            value="LC_TEMP",
            inline=True,
            style={'color': 'white'}
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

    # Filter the predicted data for the given month, day, and location
    predicted_data = predicted[(predicted["Month"] == month) & (predicted["Day"] == day) & (predicted["name"] == location)]

    # Filter the data for the year 2023
    filtered_data_2023 = filtered_data[filtered_data["Year"] == 2023]

    # Use lowess from statsmodels with custom frac and it parameters
    lowess_line = lowess(filtered_data[metric], filtered_data["Hour"], frac=0.3, it=3)
    lowess_line_2023 = lowess(filtered_data_2023[metric], filtered_data_2023["Hour"], frac=0.3, it=3)

    # Create scatter plot and add lowess line
    updated_scatter_chart = px.scatter(filtered_data, x="Hour", y=metric)
    updated_scatter_chart.add_scatter(x=lowess_line[:, 0], y=lowess_line[:, 1], mode="lines", line=dict(color="#00F2FF"), name="Trend for 2022")
    updated_scatter_chart.add_scatter(x=lowess_line_2023[:, 0], y=lowess_line_2023[:, 1], mode="lines", line=dict(color="#9900FF"), name="Trend for 2023")

    # Add the predicted data to the scatter plot
    updated_scatter_chart.add_scatter(x=predicted_data["Hour"], y=predicted_data["laeq"], mode="markers", marker=dict(color="#9900FF"), name="2023")
    updated_scatter_chart.add_scatter(x=filtered_data["Hour"], y=filtered_data[metric], mode="markers", marker=dict(color="#00F2FF"), name="2022")

    # Add reference lines
    reference_lines = {
        50: "Light traffic",
        60: "Conversational speech",
        70: "Shower",
        75: "Vacuum cleaner",
    }

    colors = ["#00FF1E", "#00D5FF", "#FB00FF", "#FF0000"]

    for (value, label), color in zip(reference_lines.items(), colors):
        updated_scatter_chart.add_trace(
            go.Scatter(
                x=[0, filtered_data["Hour"].max()],
                y=[value, value],
                mode="lines",
                line=dict(color=color),
                name=label,
                legendgroup=label,
                hoverinfo="skip"
            )
        )

    updated_scatter_chart.update_layout(
        title={'text': "Scatter chart", 'font': {'color': 'white'}},
        plot_bgcolor='#2a2d3e',
        paper_bgcolor='#2a2d3e',
        legend={'font': {'color': 'white'}},
        xaxis={'color': 'white'},
        yaxis={'color': 'white'}
    )

    return updated_scatter_chart


location = combined_df["name"]



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
        
        Input("month_slider", "value"),
        Input("day_slider", "value"),
        Input("map", "clickData"),
    ],
)


# Use the default figure when no data is available
def update_line_chart_based_on_location(month, day, clickData):
    metric = 'laeq'  
    if clickData:
        location = clickData["points"][0]["hovertext"]
        updated_scatter_chart = update_line_chart(metric, month, day, location)
        return updated_scatter_chart
    else:
        return default_fig

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
        weather_chart.update_layout(
            title={'text': "Weather chart", 'font': {'color': 'white'}},
            plot_bgcolor='#2a2d3e',
            paper_bgcolor='#2a2d3e',
            legend={'font': {'color': 'white'}},
            xaxis={'color': 'white'},
            yaxis={'color': 'white'}
        )
        return weather_chart
    else:
        return default_fig


def display_map_info(clickData, month, day):
    if clickData:
        location = clickData["points"][0]["hovertext"]
        filtered_data = combined_df[(combined_df["Month"] == month) & (combined_df["Day"] == day) & (combined_df["name"] == location)]

        if filtered_data.empty:
            return "No data available. Please select a different location or a different time point."

        # Retrieve the day name from the filtered_data DataFrame
        day_name = filtered_data['day_name'].iloc[0]
        
        # Calculate the mean noise level for the month
        mean_noise_level = combined_df[(combined_df["Month"] == month) & (combined_df["name"] == location)]["laeq"].mean()
        
        # Calculate the percentages of noise above the reference levels
        reference_lines = {
            "Light traffic": 50,
            "Conversational speech": 60,
            "Shower": 70,
            "Vacuum cleaner": 75,
        }
        noise_percents = {}
        total_points = len(filtered_data)
        for label, value in reference_lines.items():
            above_level = len(filtered_data[filtered_data["lamax"] > value])
            noise_percents[label] = round(above_level / total_points * 100, 2) if total_points > 0 else 0

        return html.Table(
        [
        html.Tr([html.Th("Date"), html.Td(f"{day_name}, {month}/{day}")]),
        html.Tr([html.Th("Noise level"), html.Td(round(filtered_data["laeq"].mean(), 2))]),
        html.Tr([html.Th("Mean Noise Level (Month)"), html.Td(round(mean_noise_level, 2))]),
        html.Tr([html.Th("Temperature"), html.Td(round(filtered_data["LC_TEMP"].mean(), 2))]),
               
        ] + [
        html.Tr([html.Th(f"{label} noise level"), html.Td(f"{percent}% of noise for your selected day")])
        for label, percent in noise_percents.items()
        ],
        style={'color': 'white'}
        )
    return "Click on a point to see more information."

def plot_occupancy(df, location, day_name):
    # Filter for  given location and day
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
    # Create bar chart for this day
    occupancy_plot = go.Figure(
        data=[
            go.Bar(
                x=hours,
                y=occupancy
            )
        ],
        layout=go.Layout(
            xaxis=dict(title="Hour"),
            yaxis=dict(title="Popularity"),
            
        ),
    )
    
    occupancy_plot.update_layout(
        title={'text': f'Occupancy for {location} on {day_name}', 'font': {'color': 'white'}},
        plot_bgcolor='#2a2d3e',
        paper_bgcolor='#2a2d3e',
        legend={'font': {'color': 'white'}},
        xaxis={'color': 'white'},
        yaxis={'color': 'white'}
    )
    return occupancy_plot


@app.callback(
    Output('occupancy_plot', 'figure'),
    [Input('map', 'clickData'),
    Input('month_slider', 'value'),
    Input('day_slider', 'value')])
def update_occupancy_plot(clickData, month_value, day_slider_value):
    if clickData:
        location = clickData["points"][0]["hovertext"]
        # Filter the DataFrame for the given location, day of the month and month
        df_location_day = combined_df[(combined_df['name'] == location) & 
                                      (combined_df['Day'] == day_slider_value) &
                                      (combined_df['Month'] == month_value)]
        # Check if we have data for this location and day
        if df_location_day.empty:
            empty_plot = go.Figure()
            empty_plot.update_layout(
                plot_bgcolor='#2a2d3e',
                paper_bgcolor='#2a2d3e',
            )
            return empty_plot
        else:
            # Get the name of the day from the 'day_name' column
            day_name = df_location_day['day_name'].iloc[0]
            return plot_occupancy(df_location_day, location, day_name)
    # If we don't have clickData or there is no data for the location, return an empty plot
    empty_plot = go.Figure()
    empty_plot.update_layout(
        plot_bgcolor='#2a2d3e',
        paper_bgcolor='#2a2d3e',
        legend={'font': {'color': 'white'}},
        xaxis={'color': 'white'},
        yaxis={'color': 'white'}
    )
    return empty_plot


@app.callback(
    Output("location_header", "children"),
    [Input("map", "clickData")],
)
def update_location_header(clickData):
    if clickData:
        location = clickData["points"][0]["hovertext"]
        return f"Location Information for {location}"
    return "Location Information"



detailed_page = html.Div([
dbc.Container(
    [
    dbc.Row(
            [
            dbc.Col(
                    [
                        html.H3("Select a point on the map to see more information", style={"color": "white"}),
                        dcc.Graph(id="map", figure=map_fig, clickData=None),
                        html.H4("Select a month you want to see", style={"color": "white"}),
                        month_bar,
                        html.H4("Select a day you want to see", style={"color": "white"}),
                        day_bar,
                        html.H3(id="location_header", children="Location Information", style={"color": "white"}),
                        html.Div(id="location_info"),
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3(id="line_chart_title", children="Line Chart for Noise Data", style={"color": "white"}),
                                        dcc.Graph(id="line_chart"),
                                    ],
                                    md=6,
                                ),
                                dbc.Col(
                                    [
                                        html.H3("Popularity Information", style={"color": "white"}),
                                        dcc.Graph(id="occupancy_plot"),
                                    ],
                                    md=6,
                                ),
                            ]
                        ),
                        html.H3(id="weather_chart_title", children="Line Chart for Weather Data", style={"color": "white"}),
                        weather_metric_buttons,
                        dcc.Graph(id="weather_chart"),
                    ],
                    md=6,
                ),
            ]
        ),
    ],
    fluid=True,
)], style=CONTENT_STYLE)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':
        return home_page
    elif pathname == '/events':
        return event_page
    elif pathname == '/detailed':
        return detailed_page
    else:
        return home_page 


if __name__ == "__main__":
    app.run_server(debug=True)