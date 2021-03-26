from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from .sparql_queries import get_all_routes, get_all_coordinates, get_all_stations, get_stations_around_coord, get_route_dep_arr
from .utils import get_distance, interSection
import folium
from folium.plugins import MarkerCluster
from flask_wtf import FlaskForm
import numpy as np
import json

bp = Blueprint('itinerary', __name__, url_prefix='/itinerary')
coordinates = get_all_coordinates()

#http://127.0.0.1:5000/itinerary/
@bp.route('/')
def upload_form():
	return render_template('itinerary/journey.html')

@bp.route('/result', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /result is accessed directly. Try going to '/http://127.0.0.1:5000/itinerary' to submit form"
    if request.method == 'POST':
        form_data = request.form
        lat_dStation = 0.0
        long_dStation = 0.0
        lat_aStation = 0.0
        long_aStation = 0.0
        dStation = form_data['dStation']
        aStation = form_data['aStation']
        for i in range(len(coordinates)):
            if coordinates[i]['name'].replace("_", " ") == dStation:
                lat_dStation = coordinates[i]['lat']
                long_dStation = coordinates[i]['long']
            if coordinates[i]['name'].replace("_", " ") == aStation:
                lat_aStation = coordinates[i]['lat']
                long_aStation = coordinates[i]['long']
        trips = []
        trips = (get_route_dep_arr(lat_dStation, long_dStation, lat_aStation, long_aStation))
        routeName = 'None'
        departure = 'None'
        map = folium.Map(location = [lat_dStation, long_dStation], zoom_start = 5, control_scale = True)
        # Add marker on origin point
        folium.Marker([lat_dStation, long_dStation], popup=dStation, icon=folium.Icon(color="red")).add_to(map)
        folium.Marker([lat_aStation, long_aStation], popup=aStation).add_to(map)
        tp = []
        if(trips):
            dtimes = []
            for trip in trips:
                if(trip['dTime'] not in dtimes): 
                    dtimes.append(trip['dTime'])
                    tmp_dict = {'routeLongName': trip['routeLongName'].replace('_', ' '), 'dTime': trip['dTime'], 'aTime': trip['aTime']}                   
                    tp.append(tmp_dict)   
            return render_template('itinerary/result.html', map=map._repr_html_(), origin = dStation, destination = aStation, trips = tp, routeName = routeName, departure = departure)
        else:
            around_dep = get_stations_around_coord(lat_dStation, long_dStation, dStation)
            around_arr = get_stations_around_coord(lat_aStation, long_aStation, aStation)
            trips, dStation, aStation = get_trips_around(around_dep, around_arr)
            map = folium.Map(location = [lat_dStation, long_dStation], zoom_start = 5, control_scale = True)
            folium.Marker([lat_dStation, long_dStation], popup=dStation, icon=folium.Icon(color="red")).add_to(map)
            folium.Marker([lat_aStation, long_aStation], popup=aStation).add_to(map)
            dtimes = []
            if(trips):
                for t in trips:
                    if (t['dTime'] not in dtimes):
                        dtimes.append(t['dTime'])
                        tmp_dict = {'routeLongName': t['routeLongName'].replace('_', ' '), 'dTime': t['dTime'], 'aTime': t['aTime']}                   
                        tp.append(tmp_dict)
                return render_template('itinerary/substitute.html', map=map._repr_html_(), origin = dStation, destination = aStation, trips = tp)
            else:
                return render_template('itinerary/no-result.html')


@bp.route('/search', methods=['POST'])
def search():
    term = request.form['q']
    #print ('term: ', term)

    stations = get_all_stations()
    stations = [s.replace('_' , ' ') for s in stations]
    #print(stations[0])

    filtered_dict = [v for v in stations if term in v]
    #print(filtered_dict)

    resp = jsonify(filtered_dict)
    resp.status_code = 200
    return resp


def get_trips_around(around_dep, around_arr):
    for i in range(len(around_arr)):
        for j in range(len(around_dep)):
            trips = (get_route_dep_arr(around_dep[j]['lat'], around_dep[j]['long'], around_arr[i]['lat'], around_arr[i]['long']))
            if(trips):
                dStation = around_dep[j]['name'].replace('_', ' ')
                aStation= around_arr[i]['name'].replace('_', ' ')
                return trips, dStation, aStation