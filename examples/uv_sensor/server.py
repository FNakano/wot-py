#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import tornado.web
import sqlite3
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application, url
from wotpy.protocols.http.server import HTTPServer
from wotpy.wot.servient import Servient
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD

HTTP_PORT = 9494
SPARQL_PORT = 8585
ID_THING = "urn:esp32"
UV_SENSOR = "uv"
DATABASE_NAME = 'observations.db'

uv_data = None

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

g = Graph()

ssn = Namespace("http://www.w3.org/ns/ssn/")
sosa = Namespace("http://www.w3.org/ns/sosa/")
ex = Namespace("http://wotpyrdfsetup.org/device/")

Observation = sosa.Observation
ResultTime = sosa.resultTime
HasResult = sosa.hasResult
Observes = sosa.observes

UVSensor = ex.UVSensor
UVObservation = ex.UVObservation
UVValue = ex.UVValue

g.add((UVSensor, RDF.type, ssn.System))
g.add((UVObservation, RDFS.subClassOf, Observation))

description = {
    "id": ID_THING,
    "name": ID_THING,
    "properties": {
        UV_SENSOR: {
            "type": "number",
            "readOnly": False,
            "observable": True
        }
    }
}

def init_db():
    """ Initialize SQLite database and table """
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS uv_observations
                     (id INTEGER PRIMARY KEY, uv_value REAL)''')
        conn.commit()

def add_to_db(value):
    """ Add UV observation to SQLite """
    with sqlite3.connect(DATABASE_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO uv_observations (uv_value) VALUES (?)", (value,))
        conn.commit()

def load_data_to_graph():
    """ Load UV observations from SQLite to RDF graph """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    for row in c.execute("SELECT id, uv_value FROM uv_observations"):
        obs_id, uv_val = row
        observation_uri = ex["Observation{}".format(obs_id)]
        g.add((observation_uri, HasResult, Literal(uv_val, datatype=UVValue)))
    conn.close()

class SPARQLHandler(tornado.web.RequestHandler):
    def post(self):
        load_data_to_graph()
        sparql_query = self.request.body.decode()
        results = g.query(sparql_query)
        self.write(results.serialize(format="json"))

class SparqlQueryHandler(RequestHandler):
    def get(self):
        self.render("sparql_query.html", results=None)

    def post(self):
        sparql_query = self.get_body_argument("sparql_query")
        results = g.query(sparql_query)
        self.render("sparql_query.html", results=results.serialize(format="json"))

class SPARQLServer(Application):
    def __init__(self):
        handlers = [
            ("/sparql", SPARQLHandler),
            ("/query", SparqlQueryHandler)
        ]
        super(SPARQLServer, self).__init__(handlers)

class CustomHTTPServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super(CustomHTTPServer, self).__init__(*args, **kwargs)

@tornado.gen.coroutine
def read_uv():
    logger.info("Lendo dados UV.")
    if uv_data is None:
        return
    uv_data_dict = json.loads(uv_data.decode("utf-8"))
    return float(uv_data_dict['uv'])

@tornado.gen.coroutine
def write_uv(value):
    global uv_data
    global g
    try:
        logger.info("Gravando dados UV.")
        uv_data = value
        uv_data_dict = json.loads(uv_data.decode("utf-8"))
        uv_val = float(uv_data_dict['uv'])
        obs_id = add_to_db(uv_val)

        observation_uri = ex["Observation{}".format(obs_id)]
        g.remove((UVSensor, Observes, None))
        g.add((UVSensor, Observes, UVObservation))
        g.add((observation_uri, HasResult, Literal(uv_val, datatype=UVValue)))

        print(g.serialize(format="turtle"))
    except Exception as e:
        logger.error(f"Erro ao gravar UV: {e}")

@tornado.gen.coroutine
def start_server():
    logger.info("Criando servidor HTTP customizado na porta: {}".format(HTTP_PORT))
    http_server = CustomHTTPServer(port=HTTP_PORT)
    servient = Servient()
    servient.add_server(http_server)
    logger.info("Iniciando servient")
    wot = yield servient.start()
    logger.info("Expondo e configurando Thing")
    exposed_thing = wot.produce(json.dumps(description))
    exposed_thing.set_property_read_handler(UV_SENSOR, read_uv)
    exposed_thing.set_property_write_handler(UV_SENSOR, write_uv)
    exposed_thing.expose()

def start_sparql_server():
    logger.info(f"Iniciando servidor SPARQL na porta: {SPARQL_PORT}")
    sparql_app = SPARQLServer()
    sparql_app.listen(SPARQL_PORT)

if __name__ == "__main__":
    init_db()
    logger.info("Iniciando loop")
    IOLoop.current().add_callback(start_server)
    IOLoop.current().add_callback(start_sparql_server)
    IOLoop.current().start()
