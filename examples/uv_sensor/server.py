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

HTTP_PORT = 9494

GLOBAL_UV_DATA = None

logging.basicConfig()
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

ID_THING = "urn:uvthing"
NAME_PROP_UV = "uv"

DESCRIPTION = {
    "id": ID_THING,
    "name": ID_THING,
    "properties": {
        NAME_PROP_UV: {
            "type": "number",
            "readOnly": False,
            "observable": True
        }
    }
}

@tornado.gen.coroutine
def uv_read_handler():
    """Custom handler for the 'UV' property."""

    LOGGER.info("Reading UV data.")
    if GLOBAL_UV_DATA is None:
        return

    uv_data_dict = json.loads(GLOBAL_UV_DATA.decode("utf-8"))
    uv_data = float(uv_data_dict['uv'])
    raise tornado.gen.Return(uv_data)

@tornado.gen.coroutine
def uv_write_handler(value):
    """Custom handler for writing UV data."""
    global GLOBAL_UV_DATA
    LOGGER.info("Writing UV data.")
    GLOBAL_UV_DATA = value
    LOGGER.info("UV data updated to: {}".format(GLOBAL_UV_DATA))

@tornado.gen.coroutine
def main():
    LOGGER.info("Creating HTTP server on: {}".format(HTTP_PORT))

    http_server = HTTPServer(port=HTTP_PORT)

    LOGGER.info("Creating servient")

    servient = Servient()
    servient.add_server(http_server)

    LOGGER.info("Starting servient")

    wot = yield servient.start()

    LOGGER.info("Exposing and configuring Thing")

    exposed_thing = wot.produce(json.dumps(DESCRIPTION))
    exposed_thing.set_property_read_handler(NAME_PROP_UV, uv_read_handler)
    exposed_thing.set_property_write_handler(NAME_PROP_UV, uv_write_handler)
    exposed_thing.expose()

if __name__ == "__main__":
    LOGGER.info("Starting loop")
    IOLoop.current().add_callback(main)
    IOLoop.current().start()
