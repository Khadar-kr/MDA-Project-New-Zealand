import pandas as pd
import overpy
import plotly.express as px

# Read noise data
noise_df = pd.read_csv('final_df.csv')
noise_df = noise_df.drop('Unnamed: 0', axis=1)

# Add coordinates for noise meters
coordinates_dict = {
    "MP 03: Naamsestraat 62 Taste": (50.87589116102767, 4.70021362494709),
    "MP 05: Calvariekapel KU Leuven": (50.874615493374556, 4.699986197958826),
    "MP 06: Parkstraat 2 La Filosovia": (50.87414576280207, 4.700087497958807),
    "MP 07: Naamsestraat 81": (50.8739265247551, 4.700117796111627),
    "MP 01: Naamsestraat 35  Maxim": (50.877203099168476, 4.7007562826177764),
    "MP 02: Naamsestraat 57 Xior": (50.8766259680261, 4.700680909605859),
    "MP08bis - Vrijthof": (50.8794917570193, 4.701099162340576),
    "MP 04: His & Hears": (50.87536619162994, 4.700165140288285),
}

university_dict = {
    "KU Leuven University": (50.877899, 4.700896),
    "KU Leuven Stuvo": (50.874844, 4.699743),
    "Department of Economics KU Leuven": (50.874893, 4.699841),
    "Ferdinand Verbiest Instituut ku Leuven": (50.875208, 4.700631),
    "Admissions Office": (50.875305, 4.700535),
    "KU Leuven Health Center": (50.874962, 4.699720),
    "Universiteitshal": (50.877949, 4.700100),
}
#
# Add latitude and longitude columns to the noise_df dataframe
noise_df['latitude'] = noise_df['description'].map(lambda x: coordinates_dict[x][0] if x in coordinates_dict else None)
noise_df['longitude'] = noise_df['description'].map(lambda x: coordinates_dict[x][1] if x in coordinates_dict else None)

# Function to get places using the Overpass API
def get_places_around(lat, lon, radius, place_types):
    overpass_api = overpy.Overpass()

    query_template = f"[out:json];("
    for place_type in place_types:
        query_template += f"""node({lat - radius}, {lon - radius}, {lat + radius}, {lon + radius})["{place_type}"];
        way({lat - radius}, {lon - radius}, {lat + radius}, {lon + radius})["{place_type}"];
        relation({lat - radius}, {lon - radius}, {lat + radius}, {lon + radius})["{place_type}"];"""
    query_template += ");(._;>;);out body;"

    result = overpass_api.query(query_template)
    return result

# Parameters for Overpass API
latitude, longitude = 50.877203099168476, 4.7007562826177764
radius = 0.0090
place_types = ["amenity=restaurant", "amenity=cafe", "shop", "building=residential", "building=accommodation", "building=commercial", "building=religious"]

# Get places around the given coordinates
result = get_places_around(latitude, longitude, radius, place_types)

# Extract data from the result object
nodes, ways = result.nodes, result.ways

# Store the results in a dictionary
def store_results_in_dict(nodes, ways):
    result_dict = {}

    for node in nodes:
        name = node.tags.get('name')
        if name and 4.699666 <= float(node.lon) <= 4.700839 and float(node.lat) <= 50.87793:
            result_dict[name] = {'latitude': float(node.lat), 'longitude': float(node.lon)}

    for way in ways:
        name = way.tags.get('name')
        if name:
            lats = [float(node.lat) for node in way.nodes]
            lons = [float(node.lon) for node in way.nodes]
            centroid_lat = sum(lats) / len(lats)
            centroid_lon = sum(lons) / len(lons)

            if 4.699666 <= centroid_lon <= 4.700839 and centroid_lat <= 50.87793:
                result_dict[name] = {'latitude': centroid_lat, 'longitude': centroid_lon}

    return result_dict

commercial_dict = store_results_in_dict(nodes, ways)

# Convert dictionary to data frame
commercial_df = pd.DataFrame.from_dict(commercial_dict, orient="index")
commercial_df["type"] = "commercial"
commercial_df.reset_index(inplace=True)
commercial_df.rename(columns={'index': 'name'}, inplace=True)

# Create a data frame for university locations
university_df = pd.DataFrame.from_dict(university_dict, orient="index", columns=["latitude", "longitude"])
university_df["type"] = "University"
university_df.reset_index(inplace=True)
university_df.rename(columns={'index': 'name'}, inplace=True)

# Update noise_df with the type column
noise_df["type"] = "noise meter"
noise_df.rename(columns={'description': 'name'}, inplace=True)

# Combine university, commercial, and noise data frames
combined_df = pd.concat([university_df, commercial_df, noise_df], ignore_index=True)


