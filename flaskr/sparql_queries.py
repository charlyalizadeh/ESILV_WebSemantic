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


def get_all_stations():
    query = build_query("""
    SELECT ?name
    WHERE {
        ?id foaf:name ?name .
    }
    GROUP BY ?name
    """)
    query_results = query_fuseki(query, 'gtfs_sncf')['results']['bindings']
    results = []
    for row in query_results:
        name = row['name']['value']
        results.append(name)
    return results


def get_all_routes():
    query = build_query("""
    SELECT DISTINCT ?route ?routeLongName ?lat ?long ?stopTime WHERE {
	?route a gtfs:Route .
  	OPTIONAL { ?route gtfs:shortName ?routeShortName . }
	OPTIONAL { ?route gtfs:longName ?routeLongName . }
  
  	?trip a gtfs:Trip .  
	?trip gtfs:service ?service .
	?trip gtfs:route ?route .
  	?stopTime a gtfs:StopTime . 
	?stopTime gtfs:trip ?trip . 
	?stopTime gtfs:stop ?stop . 
	
	?stop a gtfs:Stop . 
	?stop geo:lat ?lat .
   	?stop geo:long ?long .
    } GROUP BY ?route ?routeLongName ?lat ?long ?stopTime
    """)
    query_results = query_fuseki(query, 'gtfs_sncf')['results']['bindings']
    results = []
    #print(query_results)
    for row in query_results:
        route = row['route']['value']
        lat = float(row['lat']['value'])
        long = float(row['long']['value'])
        routeLongName = row['routeLongName']['value']
        stopTime = row['stopTime']['value']
        #print(routeLongName)
        #print(stopTime)
        results.append({'route': route, 'lat': lat, 'long': long, 'routeLongName': routeLongName, 'stopTime': stopTime})
    return results


def get_route_dep_arr(dep_lat, dep_long, arr_lat, arr_long):
    query = build_query(f"""
    SELECT DISTINCT ?route ?routeLongName ?stopTime ?aTime ?dTime ?stopTime1 ?aTime1 ?dTime1 WHERE {
    ?route a gtfs:Route .
    OPTIONAL { ?route gtfs:longName ?routeLongName . }

    ?trip a gtfs:Trip .
    ?trip gtfs:route ?route .

    ?stopTime a gtfs:StopTime .
    ?stopTime gtfs:trip ?trip .
    ?stopTime gtfs:stop ?stop .

    ?stopTime gtfs:arrivalTime ?aTime .
    ?stopTime gtfs:arrivalTime ?dTime .

    ?stop a gtfs:Stop .
    ?stop geo:lat {format(dep_lat, '.10f')} .
    ?stop geo:long {format(dep_long, '.10f')} .

    ?stop1Time1 a gtfs:StopTime .
    ?stop1Time1 gtfs:trip ?trip .
    ?stop1Time1 gtfs:stop ?stop1 .

    ?stop1Time1 gtfs:arrivalTime ?aTime1 .
    ?stop1Time1 gtfs:arrivalTime ?dTime1 .

    ?stop1 a gtfs:Stop .
    ?stop1 geo:lat {format(arr_lat, '.10f')} .
    ?stop1 geo:long {format(arr_long, '.10f')} .

    } ?route ?routeLongName ?stopTime ?aTime ?dTime ?stopTime1  ?aTime1 ?dTime1
    ORDER BY ?dTime
    """
    query_results = query_fuseki(query, 'gtfs_sncf')['results']['bindings']
    results = []
    for row in query_results:
        route = row['route']['value']
        routeLongName = row['routeLongName']['value']
        stopTime = row['stopTime']['value']
        dTime = row['dTime']['value']
        aTime = row['aTime1']['value']
        results.append({'route': route, 'aTime': aTime, 'dTime': dTime, 'routeLongName': routeLongName, 'stopTime': stopTime})
    return results

def get_stations_around_coord(lat, long, name):    
    max_lat = lat + 0.05
    max_long = long + 0.05
    min_lat = lat - 0.05
    min_long = long - 0.05
    lat, long = format(lat, '.10f'), format(long, '.10f')
    min_lat, min_long, max_lat, max_long = format(min_lat, '.10f'), format(min_long, '.10f'), format(max_lat, '.10f'), format(max_long, '.10f')
    query = build_query("""SELECT * WHERE {
        ?stop a gtfs:Stop .
        ?stop foaf:name ?name .
        ?stop geo:lat ?lat . 
        ?stop geo:long ?long .
        FILTER (?lat >= '%s' && ?lat <= '%s' && ?long >= '%s' && ?long <='%s' && ?lat != '%s' && ?long != '%s') .		
    }"""%(min_lat, max_lat, min_long, max_long, lat, long)
    )
    query_results = query_fuseki(query, 'gtfs_sncf')['results']['bindings']
    results = [{'lat': lat, 'long': long, 'name': name}]
    for row in query_results:
        name = row['name']['value']
        stop = row['stop']['value']
        lat = row['lat']['value']
        long = row['long']['value']
        results.append({'stop': stop, 'lat': lat, 'long': long, 'name': name})
    return results

def get_departures_around(lat, long, limit = 10):
    max_lat = lat + 0.05
    max_long = long + 0.05
    min_lat = lat - 0.05
    min_long = long - 0.05
    min_lat, min_long, max_lat, max_long = format(min_lat, '.10f'), format(min_long, '.10f'), format(max_lat, '.10f'), format(max_long, '.10f')
    query = build_query("""
    SELECT DISTINCT ?routeLongName ?dTime ?name ?lat ?long  WHERE {
    ?route a gtfs:Route .
    OPTIONAL { ?route gtfs:longName ?routeLongName . }

    ?trip a gtfs:Trip .  
    ?trip gtfs:route ?route .
  
    ?stopTime a gtfs:StopTime . 
    ?stopTime gtfs:trip ?trip . 
    ?stopTime gtfs:stop ?stop . 

   	?stopTime gtfs:arrivalTime ?aTime .
  	?stopTime gtfs:arrivalTime ?dTime .
  	
    ?stop a gtfs:Stop . 
    ?stop geo:lat ?lat .
    ?stop geo:long ?long .
    ?stop foaf:name ?name .
  
    ?stop1Time1 a gtfs:StopTime . 
    ?stop1Time1 gtfs:trip ?trip . 
    ?stop1Time1 gtfs:stop ?stop1 . 

   	?stop1Time1 gtfs:arrivalTime ?aTime1 .
  	?stop1Time1 gtfs:arrivalTime ?dTime1 .
  
    ?stop1 a gtfs:Stop . 
    ?stop1 foaf:name ?name1 .
  
  FILTER( ?lat >='%s' && ?lat <= '%s' && ?long >= '%s' && ?long<= '%s') .
    } GROUP BY ?routeLongName ?dTime ?name ?lat ?long
    ORDER BY ?dTime
	LIMIT %s""")%(min_lat, max_lat, min_long, max_long, str(limit))
    query_results = query_fuseki(query, 'gtfs_sncf')['results']['bindings']
    results = []
    for row in query_results:
        name = row['name']['value']
        routeLongName = row['routeLongName']['value']
        lat = row['lat']['value']
        long = row['long']['value']
        dtime = row['dTime']['value']
        results.append({'routeLongName': routeLongName, 'lat': lat, 'long': long, 'name': name, 'dTime': dtime})
    return results
