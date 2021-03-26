from math import sin, cos, sqrt, atan2, radians
import geopy
from .sparql_queries import get_all_coordinates
import folium
import numpy as np

# source: https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
def get_distance(point1, point2):
    point1 = list(point1)
    point2 = list(point2)
    R = 6373.0
    for i in (0, 1):
        point1[i] = radians(point1[i])
        point2[i] = radians(point2[i])
    dlat = point2[0] - point1[0]
    dlon = point2[1] - point1[1]
    a = sin(dlat / 2)**2 + cos(point1[0]) * cos(point2[0]) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c * 1000


def get_bounds(points):
    lats = [p[0] for p in points]
    longs = [p[1] for p in points]
    bound_sw = (min(lats), min(longs))
    bound_ne = (max(lats), max(longs))
    return (bound_sw, bound_ne)


def find_point(address):
    geolocator = geopy.Nominatim(user_agent='ESILV_WebSemantic')
    location = geolocator.geocode(address)
    if location is None:
        return
    return (location.latitude, location.longitude)


def construct_map(address, radius, datasets):
    point = find_point(address)
    if point is not None:
        coordinates = []
        map = folium.Map(location=point)
        if datasets:
            for d in datasets:
                coordinates.extend(get_all_coordinates(d))
            coordinates = [c for c in coordinates if get_distance((c['lat'], c['long']), (point[0], point[1])) < radius]
            if coordinates:
                bounds = get_bounds([(c['lat'], c['long']) for c in coordinates])
                map.fit_bounds(bounds)
            for c in coordinates:
                popuptext = '<i>\n'
                for (key, val) in c.items():
                    if key not in ('lat', 'long', 'id'):
                        popuptext += f'{key}: {c[key].replace("_", " ")}\n'
                popuptext += '</i>'
                popuphtml = folium.Html(popuptext, script=True)
                popup = folium.Popup(popuphtml, max_width=10000)
                folium.Marker([c['lat'], c['long']], popup=popup, icon=folium.Icon(color='blue', icon='glyphicon glyphicon-pause')).add_to(map)
        map.add_child(folium.LatLngPopup())
        folium.Marker(point, popup="Your location", icon=folium.Icon(color='red', icon='glyphicon glyphicon-record')).add_to(map)
        return map, point
    else:
        origin_point = (48.89608815877061, 2.235890140834457)
        map = folium.Map(location=origin_point, zoom_start=19)
        folium.Marker(origin_point, popup="Default location", icon=folium.Icon(color='red', icon='glyphicon glyphicon-record')).add_to(map)
        return map, origin_point


def interSection(arr1, arr2): # finding common elements
    # using filter method to find identical values via lambda function
    values = list(filter(lambda x: x in arr1, arr2))
    return values
