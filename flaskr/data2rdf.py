import json
from os.path import basename
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import FOAF
from rdflib import Namespace

GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
SCHEMA = Namespace("https://schema.org/")
PROJECT = Namespace('https://github.com/charlyalizadeh/ESILV_WebSemantic/')


def json_to_rdf_parking(filename, outfile=None, format='turtle'):
    placeURI = URIRef('https://schema.org/Place')
    parkingID_URI = 'https://github.com/charlyalizadeh/ESILV_WebSemantic/parking'
    if outfile is None:
        outfile = f'{basename(filename).split(".")[0]}.ttl'
    graph = Graph()
    graph.bind('foaf', FOAF)
    graph.bind('schema', SCHEMA)
    graph.bind('project', PROJECT)
    graph.bind('geo', GEO)
    with open(filename, 'r') as json_file:
        json_data_all = json.load(json_file)
        json_data = json_data_all['features']
        for p in json_data:
            properties = p['properties']
            geometry = p['geometry']
            id = URIRef(f'{parkingID_URI}/{properties.get("FID", "")}')
            graph.add((id, RDF.type, placeURI))
            graph.add((id, SCHEMA.branchCode, Literal(properties.get('FID', ''))))
            graph.add((id, SCHEMA.address, Literal(properties.get('ADRESSE_', ''))))
            graph.add((id, SCHEMA.addressCountry, Literal('France')))
            print(geometry['coordinates'])
            graph.add((id, GEO.lat, Literal(geometry['coordinates'][1])))
            graph.add((id, GEO.long, Literal(geometry['coordinates'][0])))
            graph.add((id, SCHEMA.hasMap, Literal(properties.get('STREET_VIE', ''))))
            graph.add((id, SCHEMA.isAccessibleForFree, Literal(True) if properties.get('GRATUIT_PA', '') == 'Gratuit' else Literal(False)))
            graph.add((id, SCHEMA.maximumAttendeeCapacity, Literal(properties.get('NB_PLACE', -1))))
            graph.add((id, SCHEMA.tourBookingPage, Literal(properties.get('HTTP', ''))))
            graph.add((id, FOAF.name, Literal(properties.get('NOM', ''))))
            graph.add((id, PROJECT.owner, Literal(properties.get('EXPLOITANT', ''))))
            graph.add((id, PROJECT.parkType, Literal(properties.get('TYPE_PARC', ''))))
            graph.add((id, PROJECT.creditCard, Literal(True if properties.get('REGLEMENT', '') == 'Oui' else False)))
            graph.add((id, PROJECT.freeDuration, Literal(properties.get('GRATUITE', ''))))
            graph.add((id, PROJECT.nbPmr, Literal(properties.get('NB_PMR', ''))))
            graph.add((id, PROJECT.parkSuscribeType, Literal(properties.get('TYPE', ''))))
    graph.serialize(destination=outfile, format=format)
