from wtforms import (
        Form, BooleanField, StringField,
        IntegerField, SubmitField, SelectMultipleField,
        SelectField, DateField
)
from flask_wtf import FlaskForm


class SearchMapForm(FlaskForm):
    address = StringField('Address', description='Address', render_kw={'placeholder': 'Address'})
    radius = IntegerField('Radius', description='Radius', render_kw={'placeholder': 'Radius'})
    datasets = SelectMultipleField('Datasets',
                                   description='Datasets',
                                   choices=[
                                        ('gtfs_sncf', 'gtfs_sncf'),
                                        ('gtfs_saintetiennebustram', 'gtfs_saintetiennebustram'),
                                        ('parking_argenteuil', 'parking_argenteuil')
                                    ])
    options = SelectField('Options',
                          description='Options',
                          choices=[
                              ('closest_stop', 'Closest stop'),
                              ('all_stop', 'All stop'),
                          ])
    submit = SubmitField("Search")


class SearchDeparturesForm(FlaskForm):
    address = StringField('Address', description='Adress', render_kw={'placeholder': 'Adress'})
    limit = IntegerField('Number of departures', description='Number of Departures', render_kw={'placeholder': 'Limit'})
    submit = SubmitField("Search")
