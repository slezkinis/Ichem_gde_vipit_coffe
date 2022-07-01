import os
import json
import requests
from geopy import distance
import folium
from flask import Flask


def hello_world():
    with open('map_cafes.html') as file:
        return file.read()


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance(cafe):
    return cafe['distance']


if __name__ == '__main__':
    about_cafes = []
    all_distances = []
    your_place = input('Введите ваше местоположение: ')
    apikey = os.environ['APIKEY']
    your_coords = fetch_coordinates(apikey, your_place)
    with open('coffee.json', 'r', encoding='CP1251') as my_file:
        file_cafe = my_file.read()
    file_cafe_list = json.loads(file_cafe)
    for cafe_dict in file_cafe_list:
        name_cafe = cafe_dict['Name']
        geodata_cafe_dict = cafe_dict['geoData']
        coordinates_cafe_list = geodata_cafe_dict['coordinates']
        latitude_cafe = coordinates_cafe_list[1]
        longitude_cafe = coordinates_cafe_list[0]
        distance_cafe = distance.distance(
            (your_coords[1], your_coords[0]), 
            (latitude_cafe, longitude_cafe)).km
        this_cafe_dict = {
            'title': name_cafe,
            'distance': distance_cafe,
            'latitude': latitude_cafe,
            'longitude': longitude_cafe
        }
        about_cafes.append(this_cafe_dict)
    nearest_cafes = sorted(about_cafes, key=get_distance)[:5]
    map = folium.Map([your_coords[1], your_coords[0]], zoom_start=12)
    for used_cafe_dict in nearest_cafes:
        folium.Marker([used_cafe_dict['latitude'], 
                       used_cafe_dict['longitude']], 
                      tooltip=used_cafe_dict[
                      'title']).add_to(map)
    map.save('map_cafes.html')
    app = Flask(__name__)
    app.add_url_rule('/', 'hello', hello_world)
    app.run('0.0.0.0')
