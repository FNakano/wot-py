#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import tornado.web
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application
from wotpy.protocols.http.server import HTTPServer
from wotpy.wot.servient import Servient
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.plugins.stores import berkeleydb
from datetime import datetime

HTTP_PORT = 9494
SPARQL_PORT = 8585
ID_THING = "urn:esp32"
UV_SENSOR = "uv"

uv_data = None

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

config = "berkeley_db"
store = berkeleydb.BerkeleyDB(configuration=config)
g = Graph(store=store, identifier=ID_THING)
g.open(config, create=True)

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

class SPARQLHandler(tornado.web.RequestHandler):
    def post(self):
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
    uv_data_bytes = uv_data
    if uv_data_bytes:
        uv_data_dict = json.loads(uv_data_bytes.decode("utf-8"))
        return float(uv_data_dict['uv'])

@tornado.gen.coroutine
def write_uv(value):
    global uv_data
    global g
    logger.info("Gravando dados UV.")
    uv_data = value

    uv_data_dict = json.loads(uv_data.decode("utf-8"))

    observation_id = "Observation" + datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    observation_uri = ex[observation_id]

    g.add((UVSensor, Observes, UVObservation))
    g.add((observation_uri, RDF.type, Observation))
    g.add((observation_uri, HasResult, Literal(uv_data_dict['uv'], datatype=UVValue)))
    g.add((observation_uri, ResultTime, Literal(datetime.utcnow().isoformat(), datatype=XSD.dateTime)))

    print(g.serialize(format="turtle"))

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

def close_graph():
    if store is not None:
        store.close(commit_pending_transaction=True)
    if g is not None:
        g.close()

if __name__ == "__main__":
    try:
        logger.info("Iniciando loop")
        IOLoop.current().add_callback(start_server)
        IOLoop.current().add_callback(start_sparql_server)
        IOLoop.current().start()
    finally:
        close_graph()
