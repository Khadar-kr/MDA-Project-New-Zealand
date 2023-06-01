import pandas as pd
import plotly.express as px
import pandas as pd
from collections import defaultdict

def read_popular_times_histogram(file_name):
    df = pd.read_json(file_name)
    df = df[['popularTimesHistogram']]
    df.columns = ['popularTimesHistogram']
    return df

His_Hairs_data = read_popular_times_histogram('His en hairs.json')
filosofia = read_popular_times_histogram('filosifia.json')
Maxim = read_popular_times_histogram('MAXIM occupancy.json')
Taste = read_popular_times_histogram('Taste.json')
Xior = read_popular_times_histogram('Xior.json')
kapel = read_popular_times_histogram('kapel.json')
vrijthof = read_popular_times_histogram('vrijthof.json')
naamsestraat = read_popular_times_histogram('Naamsestraat81.json')


def aggregate_histogram(df):
    combined_data = defaultdict(list)

    for index, row in df.iterrows():
        histogram = row['popularTimesHistogram']
        if pd.isna(histogram):
            continue
        for day, hours in histogram.items():
            for hour_info in hours:
                hour = hour_info['hour']
                occupancy = hour_info['occupancyPercent']
                # Append a new dictionary for each hour
                combined_data[day].append({'hour': hour, 'occupancyPercent': occupancy})

    # Convert the defaultdict to a regular dict
    combined_data = dict(combined_data)

    # Renaming the days
    day_mapping = {
        'Mo': 'Monday',
        'Tu': 'Tuesday',
        'We': 'Wednesday',
        'Th': 'Thursday',
        'Fr': 'Friday',
        'Sa': 'Saturday',
        'Su': 'Sunday'
    }

    combined_data = {day_mapping.get(k, k): v for k, v in combined_data.items()}

    return combined_data


    # First, aggregate the histograms
Xior_pop = aggregate_histogram(Xior)
Taste_pop = aggregate_histogram(Taste)
Maxim_pop = aggregate_histogram(Maxim)
filosofia_pop = aggregate_histogram(filosofia)
His_Hairs_pop = aggregate_histogram(His_Hairs_data)
kapel_pop = aggregate_histogram(kapel)
vrijthof_pop = aggregate_histogram(vrijthof)
naamsestraat_pop = aggregate_histogram(naamsestraat)

# Then, create a new DataFrame
df_pop = pd.DataFrame()

# Add each histogram as a new column
df_pop['Xior'] = [Xior_pop]
df_pop['Taste'] = [Taste_pop]
df_pop['Maxim'] = [Maxim_pop]
df_pop['filosofia'] = [filosofia_pop]
df_pop['His_Hairs'] = [His_Hairs_pop]
df_pop['kapel'] = [kapel_pop]
df_pop['vrijthof'] = [vrijthof_pop]
df_pop['naamsestraat'] = [naamsestraat_pop]

# Create a list of dictionaries for the data
data = [
    {'id': 6, 'name': 'Xior Studenthousing', 'popularTimesHistogram': Xior_pop},
    {'id': 1, 'name': 'Taste', 'popularTimesHistogram': Taste_pop},
    {'id': 5, 'name': 'Maxim', 'popularTimesHistogram': Maxim_pop},
    {'id': 3, 'name': 'La Filosovia', 'popularTimesHistogram': filosofia_pop},
    {'id': 8, 'name': 'His & Hears', 'popularTimesHistogram': His_Hairs_pop},
    {'id': 2, 'name': 'Calvariekapel KU Leuven', 'popularTimesHistogram': kapel_pop},
    {'id': 7, 'name': 'Historical Leuven Town hall', 'popularTimesHistogram': vrijthof_pop},
    {'id': 4, 'name': 'Naamsestraat 81', 'popularTimesHistogram': naamsestraat_pop}
]

# Create the DataFrame
df_pop = pd.DataFrame(data)

# Read noise data
noise_df = pd.read_csv('final_df.csv')
noise_df = noise_df.drop('Unnamed: 0', axis=1)

# Add coordinates for plaeces on the map
coordinates_dict = {
    "Taste": (50.87589116102767, 4.70021362494709),
    "Calvariekapel KU Leuven": (50.874615493374556, 4.699986197958826),
    "La Filosovia": (50.87414576280207, 4.700087497958807),
    "Naamsestraat 81": (50.8739265247551, 4.700117796111627),
    "Maxim": (50.877203099168476, 4.7007562826177764),
    "Xior Studenthousing": (50.8766259680261, 4.700680909605859),
    "Historical Leuven Town hall": (50.878761, 4.701240),
    "His & Hears": (50.87536619162994, 4.700165140288285),
}

# Dictionary to map the new names
new_names_dict = {
    'MP 03: Naamsestraat 62 Taste': 'Taste',
    'MP 05: Calvariekapel KU Leuven': 'Calvariekapel KU Leuven',
    'MP 06: Parkstraat 2 La Filosovia': 'La Filosovia',
    'MP 07: Naamsestraat 81': 'Naamsestraat 81',
    'MP 01: Naamsestraat 35  Maxim': 'Maxim',
    'MP 02: Naamsestraat 57 Xior': 'Xior Studenthousing',
    'MP08bis - Vrijthof': 'Historical Leuven Town hall',
    'MP 04: His & Hears': 'His & Hears'
}

# Rename the names in the combined_df DataFrame
noise_df['description'] = noise_df['description'].map(new_names_dict)

# Add latitude and longitude columns to the noise_df dataframe
noise_df['latitude'] = noise_df['description'].map(lambda x: coordinates_dict[x][0] if x in coordinates_dict else None)
noise_df['longitude'] = noise_df['description'].map(lambda x: coordinates_dict[x][1] if x in coordinates_dict else None)
# Convert 'Year', 'Month' and 'Day' columns to a datetime type
noise_df['date'] = pd.to_datetime(noise_df[['Year', 'Month', 'Day']])

# Create a new column 'day_name' with the day of the week
noise_df['day_name'] = noise_df['date'].dt.day_name()
noise_df.drop(['date'], axis=1, inplace=True)

# Function to convert a dictionary to a dataframe
def dict_to_dataframe(data_dict, type_str):
    df = pd.DataFrame.from_dict(data_dict, orient="index", columns=["latitude", "longitude"])
    df["type"] = type_str
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'name'}, inplace=True)
    return df

# Rename noise dataframe descritpion column to name and add type columm
noise_df.rename(columns={'description': 'name'}, inplace=True)

events_data_df = pd.read_excel('typedata.xlsx')
predicted = pd.read_csv('noise_predictions.csv')

# Merge pop_data_df and noise_df on the 'name' column
combined_df = pd.merge(noise_df, df_pop,on='name', how='left')
# Set the 'type' column in combined_df to 'Noise Meter'
combined_df['type'] = 'Noise Meter'

