from SPARQLWrapper import SPARQLWrapper, JSON
from textwrap import dedent


# TODO: Move those prefix in a SQLite database
def get_prefixes():
    return dedent("""
    PREFIX gtfs: <http://vocab.gtfs.org/terms#>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX schema: <http://schema.org/>
    PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
    PREFIX time: <http://www.w3.org/2006/time#>
    PREFIX uom: <http://www.opengis.net/def/uom/OGC/1.0/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    """)


def build_query(string):
    return get_prefixes() + dedent(string)


def query_fuseki(query, dataset):
    sparql = SPARQLWrapper(f'http://localhost:3030/{dataset}')
    print(query)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results


def get_all_coordinates(dataset,
                        rdf_class='gtfs:Stop',
                        predicates={'foaf:name': '?name'},
                        optionals={'dct:description': '?description'},
                        types={'lat': float, 'long': float}):
    query = f"""
    SELECT DISTINCT *
    WHERE {{
        ?id a {rdf_class} .
        ?id geo:long ?long .
        ?id geo:lat ?lat .
    """
    for (pred, subj) in predicates.items():
        query += f'?id {pred} {subj} .\n'
    for (pred, subj) in optionals.items():
        query += f'OPTIONAL {{ ?id {pred} {subj} . }}\n'
    query += '}'
    query = build_query(query)
    query_results = query_fuseki(query, dataset)['results']['bindings']
    results = []
    for row in query_results:
        dict_row = {}
        for (key, val) in row.items():
            val = val['value']
            if key in types.keys():
                val = types[key](val)
            dict_row[key] = val
        results.append(dict_row)
    return results
