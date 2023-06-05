import pandas as pd
import plotly.express as px
import pandas as pd
from collections import defaultdict
import requests
import boto3
import os

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


#Connection Parameters constants
aws_connection_params = {'service_name': 's3',
                        'region_name':os.getenv("AWS_DEFAULT_REGION"),
                        'aws_access_key_id':os.getenv("AWS_ACCESS_KEY_ID"),
                        'aws_secret_access_key':os.getenv("AWS_SECRET_ACCESS_KEY"),
                        'aws_bucket_name':'mdanewzealand'}


# Funtion to retrieve locations from DB
def fetchLocationsInfo():
    noiseLocations = "https://oz7iw48vm5.execute-api.eu-central-1.amazonaws.com/prod/noiselocations"
    return pd.DataFrame(requests.get(noiseLocations).json())


# Funtion to retrieve Aggregated data per event from DB By Name od the location
def fetchAggredatedDataperEventByName(name):
    eventDatabylocId = "https://bbefcz2vb7.execute-api.eu-central-1.amazonaws.com/PROD/eventaggbylocandmon?name='"+name+"'"
    return pd.DataFrame(requests.get(eventDatabylocId).json())

# Funtion to retrieve Aggregated data per event from DB
def fetchAggredatedDataperEvent():
    eventDatabylocId = "https://bbefcz2vb7.execute-api.eu-central-1.amazonaws.com/PROD/eventaggbylocandmon"
    return pd.DataFrame(requests.get(eventDatabylocId).json())

# Funtion to fetch connection to S3 Bucket #AWS
def fetchS3Bucket():
    s3 = boto3.resource(
    service_name=aws_connection_params.get('service_name'),
    region_name=aws_connection_params.get('region_name'),
    aws_access_key_id=aws_connection_params.get('aws_access_key_id'),
    aws_secret_access_key=aws_connection_params.get('aws_secret_access_key'))
    return s3.Bucket(aws_connection_params.get('aws_bucket_name'))

# Funtion to retrieve  data from S3 Bucket #AWS
def fetchDataFromS3File(fileName):
    s3Bucket.download_file(Key=fileName, Filename=fileName)
    noise_dataframe=pd.read_csv(fileName)
    return noise_dataframe


# def fetchallData():
locationsData = fetchLocationsInfo()
s3Bucket = fetchS3Bucket()
eventsData = fetchAggredatedDataperEvent()
noiseData=fetchDataFromS3File("noise_data_final.csv")
predictions_data=fetchDataFromS3File("noise_predictions.csv")

LOCATIONS_INFO = locationsData
EVENT_DATA = eventsData
NOISE_DATA=noiseData
PREDICTED_DATA=predictions_data

# Read noise data
noise_df = NOISE_DATA
noise_df = noise_df.drop('id', axis=1)


# Add latitude and longitude columns to the noise_df dataframe
locations_copy = LOCATIONS_INFO.drop('name',axis=1)
noise_df = pd.merge(noise_df,locations_copy,on='loc_id',how = 'left')

# Convert 'Year', 'Month' and 'Day' columns to a datetime type
noise_df['date'] = pd.to_datetime(noise_df[['Year', 'Month', 'Day']])

# Create a new column 'day_name' with the day of the week
noise_df['day_name'] = noise_df['date'].dt.day_name()
noise_df.drop(['date'], axis=1, inplace=True)

# # Function to convert a dictionary to a dataframe
# def dict_to_dataframe(data_dict, type_str):
#     df = pd.DataFrame.from_dict(data_dict, orient="index", columns=["latitude", "longitude"])
#     df["type"] = type_str
#     df.reset_index(inplace=True)
#     df.rename(columns={'index': 'name'}, inplace=True)
#     return df

# Rename noise dataframe descritpion column to name and add type columm
# noise_df.rename(columns={'description': 'name'}, inplace=True)

# events_data_df = pd.read_excel('typedata.xlsx')
events_data_df  = EVENT_DATA
predicted = PREDICTED_DATA

# Merge pop_data_df and noise_df on the 'name' column
combined_df = pd.merge(noise_df, df_pop,on='name', how='left')
# Set the 'type' column in combined_df to 'Noise Meter'
combined_df['type'] = 'Noise Meter'

