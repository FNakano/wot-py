#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WoT application to expose a Thing that provides UV sensor values.
"""

import json
import logging
import tornado.gen
from tornado.ioloop import IOLoop
from wotpy.protocols.http.server import HTTPServer
from wotpy.wot.servient import Servient
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS

# Constants
HTTP_PORT = 9494
ID_THING = "urn:esp32"
UV_SENSOR = "uv"

# Global data storage
uv_data = None

# Setup logger
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# RDF setup
g = Graph()
n = Namespace("http://wotpyrdfsetup.org/device/")
Device = n.Device
UVSensor = n.UVSensor
hasReading = n.hasReading
sensor1 = n.sensor1

# Create the class hierarchy
g.add((UVSensor, RDFS.subClassOf, Device))

# Thing description
description = {
    "id": ID_THING,
    "name": ID_THING,
    "properties": {
        UV_SENSOR: {
            "type": "number",
            "readOnly": False,
            "observable": True
        }
        # Add more sensors as needed
    }
}

@tornado.gen.coroutine
def read_uv():
    """Custom handler for the 'UV' property."""
    logger.info("Reading UV data.")
    if uv_data is None:
        return
    uv_data_dict = json.loads(uv_data.decode("utf-8"))
    return float(uv_data_dict['uv'])

@tornado.gen.coroutine
def write_uv(value):
    """Custom handler for writing UV data."""
    global uv_data
    global g
    logger.info("Writing UV data.")
    uv_data = value
    logger.info("UV data updated to: {}".format(uv_data))

    # Update the graph
    g.remove((sensor1, hasReading, None))  # remove old reading
    uv_data_dict = json.loads(uv_data.decode("utf-8"))
    g.add((sensor1, RDF.type, UVSensor))
    g.add((sensor1, hasReading, Literal(uv_data_dict['uv'])))

    print(g.serialize(format="turtle"))  # print the graph for debugging

# Add handlers for other sensors as needed

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
    # Add handlers for other sensors as needed
    exposed_thing.expose()

if __name__ == "__main__":
    logger.info("Starting loop")
    IOLoop.current().add_callback(start_server)
    IOLoop.current().start()
