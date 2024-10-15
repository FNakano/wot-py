e5d22008c11c
docker container run --network host -it --rm --user 1000:1000 -v $PWD/examples/uv_sensor:/app e5d22008c11c sh

select * where {?s ?p ?o}


{"results": {"bindings": [{"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212124320812210"}, "p": {"type": "uri", "value": "http://www.w3.org/ns/sosa/hasResult"}, "o": {"type": "literal", "value": "31", "datatype": "http://wotpyrdfsetup.org/device/UVValue"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212124320812210"}, "p": {"type": "uri", "value": "http://www.w3.org/ns/sosa/resultTime"}, "o": {"type": "literal", "value": "2023-12-12T12:43:20.813586", "datatype": "http://www.w3.org/2001/XMLSchema#dateTime"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212124320812210"}, "p": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"}, "o": {"type": "uri", "value": "http://www.w3.org/ns/sosa/Observation"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212125340932377"}, "p": {"type": "uri", "value": "http://www.w3.org/ns/sosa/hasResult"}, "o": {"type": "literal", "value": "30", "datatype": "http://wotpyrdfsetup.org/device/UVValue"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212125340932377"}, "p": {"type": "uri", "value": "http://www.w3.org/ns/sosa/resultTime"}, "o": {"type": "literal", "value": "2023-12-12T12:53:40.933381", "datatype": "http://www.w3.org/2001/XMLSchema#dateTime"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212125340932377"}, "p": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"}, "o": {"type": "uri", "value": "http://www.w3.org/ns/sosa/Observation"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/UVSensor"}, "p": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"}, "o": {"type": "uri", "value": "http://www.w3.org/ns/ssn/System"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/UVSensor"}, "p": {"type": "uri", "value": "http://www.w3.org/ns/sosa/observes"}, "o": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/UVObservation"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212130248755052"}, "p": {"type": "uri", "value": "http://www.w3.org/ns/sosa/hasResult"}, "o": {"type": "literal", "value": "29", "datatype": "http://wotpyrdfsetup.org/device/UVValue"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212130248755052"}, "p": {"type": "uri", "value": "http://www.w3.org/ns/sosa/resultTime"}, "o": {"type": "literal", "value": "2023-12-12T13:02:48.756074", "datatype": "http://www.w3.org/2001/XMLSchema#dateTime"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212130248755052"}, "p": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"}, "o": {"type": "uri", "value": "http://www.w3.org/ns/sosa/Observation"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/UVObservation"}, "p": {"type": "uri", "value": "http://www.w3.org/2000/01/rdf-schema#subClassOf"}, "o": {"type": "uri", "value": "http://www.w3.org/ns/sosa/Observation"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231120005521408626"}, "p": {"type": "uri", "value": "http://www.w3.org/ns/sosa/hasResult"}, "o": {"type": "literal", "value": "3989", "datatype": "http://wotpyrdfsetup.org/device/UVValue"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231120005521408626"}, "p": {"type": "uri", "value": "http://www.w3.org/ns/sosa/resultTime"}, "o": {"type": "literal", "value": "2023-11-20T00:55:21.409298", "datatype": "http://www.w3.org/2001/XMLSchema#dateTime"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231120005521408626"}, "p": {"type": "uri", "value": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"}, "o": {"type": "uri", "value": "http://www.w3.org/ns/sosa/Observation"}}]}, "head": {"vars": ["s", "p", "o"]}}

prefix sosa: <http://www.w3.org/ns/sosa/>
select * where {?s a sosa:Observation}

{"results": {"bindings": [{"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212124320812210"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212125340932377"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231212130248755052"}}, {"s": {"type": "uri", "value": "http://wotpyrdfsetup.org/device/Observation20231120005521408626"}}]}, "head": {"vars": ["s"]}}

prefix sosa: <http://www.w3.org/ns/sosa/>
select * where {?s sosa:hasResult ?o}

{
  "results": {
    "bindings": [
      {
        "s": {
          "type": "uri",
          "value": "http://wotpyrdfsetup.org/device/Observation20231120005521408626"
        },
        "o": {
          "type": "literal",
          "value": "3989",
          "datatype": "http://wotpyrdfsetup.org/device/UVValue"
        }
      },
      {
        "s": {
          "type": "uri",
          "value": "http://wotpyrdfsetup.org/device/Observation20231212124320812210"
        },
        "o": {
          "type": "literal",
          "value": "31",
          "datatype": "http://wotpyrdfsetup.org/device/UVValue"
        }
      },
      {
        "s": {
          "type": "uri",
          "value": "http://wotpyrdfsetup.org/device/Observation20231212125340932377"
        },
        "o": {
          "type": "literal",
          "value": "30",
          "datatype": "http://wotpyrdfsetup.org/device/UVValue"
        }
      },
      {
        "s": {
          "type": "uri",
          "value": "http://wotpyrdfsetup.org/device/Observation20231212130248755052"
        },
        "o": {
          "type": "literal",
          "value": "29",
          "datatype": "http://wotpyrdfsetup.org/device/UVValue"
        }
      }
    ]
  },
  "head": {
    "vars": [
      "s",
      "o"
    ]
  }
}

