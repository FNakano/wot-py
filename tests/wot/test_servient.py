#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import uuid

import pytest
import tornado.gen
import tornado.httpclient
import tornado.ioloop
import tornado.websocket
from faker import Faker

from tests.utils import find_free_port
from wotpy.protocols.ws.server import WebsocketServer
from wotpy.wot.constants import WOT_TD_CONTEXT_URL
from wotpy.wot.consumed.thing import ConsumedThing
from wotpy.wot.servient import Servient
from wotpy.wot.td import ThingDescription


def test_servient_td_catalogue():
    """The servient provides a Thing Description catalogue HTTP endpoint."""

    catalogue_port = find_free_port()

    servient = Servient()
    servient.catalogue_port = catalogue_port

    @tornado.gen.coroutine
    def start():
        raise tornado.gen.Return((yield servient.start()))

    wot = tornado.ioloop.IOLoop.current().run_sync(start)

    td_doc_01 = {
        "id": uuid.uuid4().urn,
        "name": Faker().sentence(),
        "properties": {
            "status": {
                "description": "Shows the current status of the lamp",
                "type": "string",
                "forms": [{
                    "href": "coaps://mylamp.example.com:5683/status"
                }]
            }
        }
    }

    td_doc_02 = {
        "id": uuid.uuid4().urn,
        "name": Faker().sentence()
    }

    td_01_str = json.dumps(td_doc_01)
    td_02_str = json.dumps(td_doc_02)

    exposed_thing_01 = wot.produce(td_01_str)
    exposed_thing_02 = wot.produce(td_02_str)

    exposed_thing_01.expose()
    exposed_thing_02.expose()

    @tornado.gen.coroutine
    def test_coroutine():
        http_client = tornado.httpclient.AsyncHTTPClient()

        catalogue_url = "http://localhost:{}/".format(catalogue_port)
        catalogue_url_res = yield http_client.fetch(catalogue_url)
        urls_map = json.loads(catalogue_url_res.body)

        assert len(urls_map) == 2
        assert exposed_thing_01.thing.url_name in urls_map.get(td_doc_01["id"])
        assert exposed_thing_02.thing.url_name in urls_map.get(td_doc_02["id"])

        thing_01_url = "http://localhost:{}{}".format(catalogue_port, urls_map[td_doc_01["id"]])
        thing_01_url_res = yield http_client.fetch(thing_01_url)
        td_doc_01_recovered = json.loads(thing_01_url_res.body)

        assert td_doc_01_recovered["id"] == td_doc_01["id"]
        assert td_doc_01_recovered["name"] == td_doc_01["name"]

        catalogue_expanded_url = "http://localhost:{}/?expanded=true".format(catalogue_port)
        cataligue_expanded_url_res = yield http_client.fetch(catalogue_expanded_url)
        expanded_map = json.loads(cataligue_expanded_url_res.body)

        num_props = len(td_doc_01.get("properties", {}).keys())

        assert len(expanded_map) == 2
        assert td_doc_01["id"] in expanded_map
        assert td_doc_02["id"] in expanded_map
        assert len(expanded_map[td_doc_01["id"]]["properties"]) == num_props

        yield servient.shutdown()

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_servient_start_stop():
    """The servient and contained ExposedThings can be started and stopped."""

    fake = Faker()

    ws_port = find_free_port()
    ws_server = WebsocketServer(port=ws_port)

    servient = Servient()
    servient.disable_td_catalogue()
    servient.add_server(ws_server)

    @tornado.gen.coroutine
    def start():
        raise tornado.gen.Return((yield servient.start()))

    wot = tornado.ioloop.IOLoop.current().run_sync(start)

    thing_id = uuid.uuid4().urn
    name_prop_string = fake.user_name()
    name_prop_boolean = fake.user_name()

    td_doc = {
        "id": thing_id,
        "name": Faker().sentence(),
        "properties": {
            name_prop_string: {
                "observable": True,
                "type": "string"
            },
            name_prop_boolean: {
                "observable": True,
                "type": "boolean"
            }
        }
    }

    td_str = json.dumps(td_doc)

    exposed_thing = wot.produce(td_str)
    exposed_thing.expose()

    value_boolean = fake.pybool()
    value_string = fake.pystr()

    @tornado.gen.coroutine
    def get_property(prop_name):
        """Gets the given property using the WS Link contained in the thing description."""

        td = ThingDescription.from_thing(exposed_thing.thing)
        consumed_thing = ConsumedThing(servient, td=td)

        value = yield consumed_thing.read_property(prop_name)

        raise tornado.gen.Return(value)

    @tornado.gen.coroutine
    def assert_thing_active():
        """Asserts that the retrieved property values are as expected."""

        retrieved_boolean = yield get_property(name_prop_boolean)
        retrieved_string = yield get_property(name_prop_string)

        assert retrieved_boolean == value_boolean
        assert retrieved_string == value_string

    @tornado.gen.coroutine
    def test_coroutine():
        yield exposed_thing.write_property(name=name_prop_boolean, value=value_boolean)
        yield exposed_thing.write_property(name=name_prop_string, value=value_string)

        yield assert_thing_active()

        exposed_thing.destroy()

        with pytest.raises(Exception):
            yield assert_thing_active()

        with pytest.raises(Exception):
            exposed_thing.expose()

        yield servient.shutdown()

    tornado.ioloop.IOLoop.current().run_sync(test_coroutine)


def test_duplicated_thing_names():
    """A Servient rejects Things with duplicated IDs."""

    description_01 = {
        "@context": [WOT_TD_CONTEXT_URL],
        "id": uuid.uuid4().urn,
        "name": Faker().sentence()
    }

    description_02 = {
        "@context": [WOT_TD_CONTEXT_URL],
        "id": uuid.uuid4().urn,
        "name": Faker().sentence()
    }

    description_03 = {
        "@context": [WOT_TD_CONTEXT_URL],
        "id": description_01.get("id"),
        "name": Faker().sentence()
    }

    description_01_str = json.dumps(description_01)
    description_02_str = json.dumps(description_02)
    description_03_str = json.dumps(description_03)

    servient = Servient()
    servient.disable_td_catalogue()

    @tornado.gen.coroutine
    def start():
        raise tornado.gen.Return((yield servient.start()))

    wot = tornado.ioloop.IOLoop.current().run_sync(start)

    wot.produce(description_01_str)
    wot.produce(description_02_str)

    with pytest.raises(ValueError):
        wot.produce(description_03_str)

    @tornado.gen.coroutine
    def shutdown():
        yield servient.shutdown()

    tornado.ioloop.IOLoop.current().run_sync(shutdown)
