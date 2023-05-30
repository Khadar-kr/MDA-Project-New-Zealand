import pandas as pd
import plotly.express as px

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


google_data = pd.read_json('data_google_2.json')
google_data.drop(['imagesCount', 'webResults', 'reviews', 'reviewsTags', 'orderBy', 
         'questionsAndAnswers', 'updatesFromCustomers', 'reserveTableUrl',
           'placesTags', 'subTitle','description','price','menu',
          'locatedIn'	,'neighborhood'	,'street','city','postalCode','state','countryCode',
          'plusCode',	'website',	'phone',	'temporarilyClosed',	'claimThisBusiness',
          'permanentlyClosed',	'totalScore',	'placeId',	'categories',	'cid',	'url',	'scrapedAt',
          	'popularTimesLiveText',	'popularTimesLivePercent',
            'peopleAlsoSearch',	'additionalInfo',	'reviewsCount',	'reviewsDistribution', 'address' 	
          ], axis=1, inplace=True)
#google_data['type']= google_data['categoryName']
google_data['name']= google_data['title']
google_data.drop(['categoryName','title'], axis=1, inplace=True)
#google_data['type'] = google_data['type'].replace({'Brunch restaurant': 'Restaurant',
                                 #'Italian restaurant': 'Restaurant',
                                 #'Vegan restaurant': 'Restaurant',
                                 #'Turkish restaurant': 'Restaurant',
                                 #'Sushi restaurant': 'Restaurant',
                                 #'Fine dining restaurant': 'Restaurant',
                                 #'Egyptian restaurant': 'Restaurant',
                                 #'Fast food restaurant': 'Restaurant',
                                 #'Cafe': 'Bar',})
#google_data['latitude'] = google_data['location'].apply(lambda x: x['lat'])
#google_data['longitude'] = google_data['location'].apply(lambda x: x['lng'])
google_data.drop(['location'], axis=1, inplace=True)


# Dictionary to map the new names
new_names_dict = {
    'Taste': 'Taste',
    'Calvariekapel': 'Calvariekapel KU Leuven',
    'La Filosofia': 'La Filosovia',
    'Maxim': 'Maxim',
    'Xior Studenthousing': 'Xior Studenthousing',
    'Historical Leuven Town hall': 'Historical Leuven Town hall',
    'His & Hairs': 'His & Hears'
}
google_data['name'] = google_data['name'].map(new_names_dict)
new_row = pd.DataFrame({'name': ['Naamsestraat 81']})
google_data = pd.concat([google_data, new_row], ignore_index=True)

# Merge google_data and noise_df on the 'name' column
combined_df = pd.merge(google_data, noise_df, on='name', how='left')

# Set the 'type' column in combined_df to 'Noise Meter'
combined_df['type'] = 'Noise Meter'

events_data_df = pd.read_excel('typedata.xlsx')

