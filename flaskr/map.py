from flask import (
        Blueprint, redirect, render_template, request, url_for
)
import folium
from .forms import SearchMapForm
from .utils import construct_map
bp = Blueprint('map', __name__, url_prefix='/map')


@bp.route('/stops/<float:lat>/<float:long>/<int:radius>', methods=['GET', 'POST'])
def stops(lat, long, radius):
    form = SearchMapForm(datasets=['gtfs_sncf'],
                         options=['all_stop'])
    map = folium.Map(location=(48.89608815877061, 2.235890140834457), zoom_start=19)
    map.add_child(folium.LatLngPopup())
    if form.validate_on_submit():
        address = form.address.data
        radius = form.radius.data
        datasets = form.datasets.data
        options = form.options.data
        map, point = construct_map(address, radius, datasets, options)
        redirect(url_for('map.stops', lat=point[0], long=point[1], radius=radius))
    return render_template('map/stops.html', map=map._repr_html_(), form=form)
