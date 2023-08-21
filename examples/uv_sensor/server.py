#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import tornado.gen
from tornado.ioloop import IOLoop
from wotpy.protocols.http.server import HTTPServer
from wotpy.wot.servient import Servient
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, XSD

HTTP_PORT = 9494
ID_THING = "urn:esp32"
UV_SENSOR = "uv"

uv_data = None

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

g = Graph()

# SSN ontology definitions
ssn = Namespace("http://www.w3.org/ns/ssn/")
sosa = Namespace("http://www.w3.org/ns/sosa/")
ex = Namespace("http://wotpyrdfsetup.org/device/")

Observation = sosa.Observation
ResultTime = sosa.resultTime
HasResult = sosa.hasResult
Observes = sosa.observes

UVSensor = ex.UVSensor  # A specific sensor instance
UVObservation = ex.UVObservation  # An observation class
UVValue = ex.UVValue  # Observed value

g.add((UVSensor, RDF.type, ssn.System))
g.add((UVObservation, RDFS.subClassOf, Observation))
g.add((UVValue, RDFS.datatype, XSD.float))

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

@tornado.gen.coroutine
def read_uv():
    logger.info("Reading UV data.")
    if uv_data is None:
        return
    uv_data_dict = json.loads(uv_data.decode("utf-8"))
    return float(uv_data_dict['uv'])

@tornado.gen.coroutine
def write_uv(value):
    global uv_data
    global g
    logger.info("Writing UV data.")
    uv_data = value
    logger.info("UV data updated to: {}".format(uv_data))

    uv_data_dict = json.loads(uv_data.decode("utf-8"))

    observation_uri = ex["Observation{}".format(uv_data_dict['uv'])]

    g.remove((UVSensor, Observes, None))
    g.add((UVSensor, Observes, UVObservation))
    g.add((observation_uri, HasResult, Literal(uv_data_dict['uv'], datatype=UVValue)))

    print(g.serialize(format="turtle"))

@tornado.gen.coroutine
def start_server():
    logger.info("Creating HTTP server on: {}".format(HTTP_PORT))
    http_server = HTTPServer(port=HTTP_PORT)
    logger.info("Creating servient")
    servient = Servient()
    servient.add_server(http_server)
    logger.info("Starting servient")
    wot = yield servient.start()
    logger.info("Exposing and configuring Thing")
    exposed_thing = wot.produce(json.dumps(description))
    exposed_thing.set_property_read_handler(UV_SENSOR, read_uv)
    exposed_thing.set_property_write_handler(UV_SENSOR, write_uv)
    exposed_thing.expose()

if __name__ == "__main__":
    logger.info("Starting loop")
    IOLoop.current().add_callback(start_server)
    IOLoop.current().start()
