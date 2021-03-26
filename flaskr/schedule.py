from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from .sparql_queries import get_departures_around, get_all_coordinates
from .utils import get_distance, interSection, find_point, get_bounds
import folium
from folium.plugins import MarkerCluster
from flask_wtf import FlaskForm
import numpy as np
import json
from .forms import SearchDeparturesForm

bp = Blueprint('schedule', __name__, url_prefix='/schedule')

#http://127.0.0.1:5000/schedule/
@bp.route('/schedule/<float:lat>/<float:long>/<int:limit>', methods=['GET', 'POST'])
def schedule(lat, long, limit, radius = 10000):
    form = SearchDeparturesForm(request.form)
    map = folium.Map(location=(48.89608815877061, 2.235890140834457), zoom_start=19)
    map.add_child(folium.LatLngPopup())
    trips = []
    tp = []
    if request.method == 'POST' and form.validate():
        address = form.address.data
        point = find_point(address)
        limit = form.limit.data
        #print(point)
        if point is not None:
            #radius = form.radius.data
            coordinates = get_all_coordinates()
            coordinates = [c for c in coordinates if get_distance((c['lat'], c['long']), (point[0], point[1])) < radius]
            map = folium.Map(location=point)
            if coordinates:
                bounds = get_bounds([(c['lat'], c['long']) for c in coordinates])
                map.fit_bounds(bounds)
            map.add_child(folium.LatLngPopup())
            for c in coordinates:
                folium.Marker([c['lat'], c['long']], popup=f'<i>{c["name"].replace("_", " ")}</i>').add_to(map)
            trips = get_departures_around(point[0], point[1], limit)
            dtimes = []
            for t in trips:
                    if (t['dTime'] not in dtimes):
                        dtimes.append(t['dTime'])
                        tmp_dict = {'routeLongName': t['routeLongName'].replace('_', ' '), 'dTime': t['dTime'], 'dStation' : t['name'].replace('_', ' ')}                   
                        tp.append(tmp_dict)
                        folium.Marker([t['lat'], t['long']], popup=f'<i>{t["name"].replace("_", " ")}</i>').add_to(map)
            redirect(url_for('schedule.schedule', lat=point[0], long=point[1], limit = limit, trips = tp))
    return render_template('schedule/schedule.html', map=map._repr_html_(), form=form, trips = tp)
