# -*- coding: utf-8 -*-
"""AnalisedeDadosGeoJSON

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XhpTTypjxtacH1RxtCP0xovDVe5rxbPe
"""
# Task1

import pandas as pd
import geojson
from PIL import ImageColor

# Reading files into separate DataFrames
routes_df = pd.read_csv('/metro/routes.txt')
shapes_df = pd.read_csv('metro/shapes.txt')
stops_df = pd.read_csv('metro/stops.txt')

# Renaming the "shape_id" column to "route_id" in shapes
shapes_df.rename(columns={'shape_id': 'route_id'}, inplace=True)

# Merging DataFrames using "route_id" as the key
merged_data = pd.merge(shapes_df, routes_df, on='route_id')
merged_data = pd.merge(merged_data, stops_df, left_on=['shape_pt_lat', 'shape_pt_lon'], right_on=['stop_lat', 'stop_lon'])

merged_data

def drawMetro():
    features = []
    for _, group in merged_data.groupby('route_short_name'): 
        group = group.sort_values('shape_pt_sequence')

        coordinates = []

        for _, row in group.iterrows():
            lon = row['stop_lon']
            lat = row['stop_lat']

            point = geojson.Point((lon, lat))

            # Metainformation: station name
            properties = {
                'stop_name': row['stop_name']
            }

            # Create a feature with the Point object and properties.
            feature = geojson.Feature(geometry=point, properties=properties)
            features.append(feature)
            coordinates.append((lon, lat))

        color ='#'+group['route_color'].values[0]

        linestring = geojson.LineString(coordinates) 

        #  Metadata: line name and color
        properties = {
            'route_short_name': group['route_short_name'].values[0],
            "stroke": color
        }

        # Create a feature with the LineString object and properties
        feature = geojson.Feature(geometry=linestring, properties=properties, stroke=color)
        features.append(feature)

    # Create the FeatureCollection object with the list of features
    feature_collection = geojson.FeatureCollection(features)

    # Write the FeatureCollection object to the "metro.geojson" file
    with open('metro.geojson', 'w') as f:
        geojson.dump(feature_collection, f)

drawMetro()

#Task 2

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic

pip install geopy

def create_subway_graph(data):
    G = nx.Graph()

    # Add edges between stations and lines
    for _, row in data.iterrows():
        station = row['stop_name']
        line = row['route_short_name']
        G.add_edge(station, line)
    return G
G=create_subway_graph(merged_data)
plt.figure(figsize=(12, 8))
nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', font_size=10, node_size=500)
plt.title("Grafo de Conexões de Estações de Metrô")
plt.show()

def hubPorto(data):
    # Add edges between stations and lines
    stations = data.groupby('stop_name')['route_short_name'].nunique()

    # Find the station with the most lines
    station_plus_lines = stations.idxmax()

    # Get the lines associated with the station with the most lines
    lines = set(data[data['stop_name'] == station_plus_lines]['route_short_name'])

    return station_plus_lines, lines
hubPorto(merged_data)

def directPathExists(origin, destination, graph):
    lines_station1 = set(graph.neighbors(station1))
    lines_station2 = set(graph.neighbors(station2))
    common_lines = lines_station1.intersection(lines_station2)
    return len(common_lines) > 0

# Tests
station1 = 'Camara de Matosinhos'
station2 = 'I.P.O.'
directPathExists(station1, station2, create_subway_graph(merged_data))

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic
def calculate_travel_time(distance):
    speed = 30  # km/h
    time_per_km = 1 / (speed / 60)  # minutes per km
    time = distance * time_per_km + 5  # add 5 minutes for line transfer
    return time * 60  # convert minutes to seconds

def fastestWay(station1, station2, graph, data):
    location_data = data[['stop_name', 'stop_lat', 'stop_lon']].drop_duplicates(subset='stop_name')
    station1_data = location_data[location_data['stop_name'] == station1].iloc[0]
    station2_data = location_data[location_data['stop_name'] == station2].iloc[0]

    distance = geodesic((station1_data['stop_lat'], station1_data['stop_lon']),
                        (station2_data['stop_lat'], station2_data['stop_lon'])).kilometers

    estimated_time = calculate_travel_time(distance)
    return estimated_time

station1 = 'Casa da Musica'
station2 = 'Hospital de Sao Joao'
fastestWay(station1, station2, create_subway_graph(merged_data), merged_data)
