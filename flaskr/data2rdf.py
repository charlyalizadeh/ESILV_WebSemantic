import json
from os.path import basename
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import FOAF
from rdflib import Namespace

GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
SCHEMA = Namespace("https://schema.org/")
PROJECT = Namespace('https://github.com/charlyalizadeh/ESILV_WebSemantic/')


def json_to_jsonld_parking(parking_json):
    properties = parking_json['properties']
    geometry = parking_json['geometry']
    return {
        '@context': 'https://schema.org/Place',
        '@id': f'https://github.com/charlyalizadeh/ESILV_WebSemantic/parking/{parking_json["properties"]["FID"]}',
        "branchCode": properties.get('FID', ''),
        "_OriginalId": properties.get('ID', ''),
        "geo": {
            "address": properties.get('ADRESSE_', ''),
            "addressCountry": "France",
            "latitude": geometry['coordinates'][0],
            "longitude": geometry['coordinates'][1]
        },
        "isAccessibleForFree": True if properties.get('GRATUIT_PA', '') == "Gratuit" else False,
        "maximumAttendeeCapacity": properties.get('NB_PLACE', ''),
        "tourBookingPage": properties.get('HTTP', ''),
        "name": properties.get('NOM', ''),
        "disambiguatingDescription": "A place to park cars",
        "suscriberOnly": True if properties.get('TYPE', '') == "Abonnés" else False,
        "parkingType": properties.get('TYPE_PARC', ''),
        "reglement": properties.get('REGLEMENT', '') == "Oui",
        "freeParkDuration": properties.get('GRATUITE', ''),
        "streetView": properties.get('STREET_VIE', ''),
        "owner": properties.get('EXPLOITANT', ''),
        "nbPmr": properties.get('NB_PMR', '')
    }


def json_to_jsonld_parking_file(filename, outfile=None):
    if outfile is None:
        outfile = f'{basename(filename).split(".")[0]}_ld.json'
    with (open(filename, 'r') as json_file,
          open(outfile, 'w') as jsonld_file):
        parkings = json.load(json_file)['features']
        for p in parkings:
            jsonld_data = json_to_jsonld_parking(p)
            json.dump(jsonld_data, jsonld_file)
            jsonld_file.write('\n')


def jsonld_to_rdf_parking(filename, outfile=None):
    if outfile is None:
        outfile = f'{basename(filename).split(".")[0]}.txt'
    g = Graph()
    with open(filename, 'r') as jsonld_file:
        for line in jsonld_file.readlines():
            context = json.loads(line)
            gg


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
