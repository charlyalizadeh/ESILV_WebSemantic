from wtforms import Form, BooleanField, StringField, IntegerField, SubmitField, SelectMultipleField
from flask_wtf import FlaskForm


class SearchMapForm(FlaskForm):
    address = StringField('Address', description='Adress', render_kw={'placeholder': 'Adress'})
    radius = IntegerField('Radius', description='Radius', render_kw={'placeholder': 'Radius'})
    datasets = SelectMultipleField('Datasets', description='Datasets', choices=[('gtfs_sncf', 'gtfs_sncf'), ('gtfs_saintetiennebustram', 'gtfs_saintetiennebustram')])
    submit = SubmitField("Search")
