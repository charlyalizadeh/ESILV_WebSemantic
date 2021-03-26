import functools

from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import folium
from folium.plugins import MarkerCluster
from .sparql_queries import get_all_coordinates
from .utils import get_distance, get_bounds, find_point, construct_map
from .forms import SearchMapForm
bp = Blueprint('map', __name__, url_prefix='/map')


@bp.route('/sncf-stops/<float:lat>/<float:long>/<int:radius>', methods=['GET', 'POST'])
def sncf_stops(lat, long, radius):
    form = SearchMapForm(request.form)
    map = folium.Map(location=(48.89608815877061, 2.235890140834457), zoom_start=19)
    map.add_child(folium.LatLngPopup())
    if request.method == 'POST' and form.validate():
        address = form.address.data
        radius = form.radius.data
        datasets = form.datasets.data
        map, point = construct_map(address, radius, datasets)
        redirect(url_for('map.sncf_stops', lat=point[0], long=point[1], radius=radius))
    return render_template('map/sncf-stops.html', map=map._repr_html_(), form=form)
