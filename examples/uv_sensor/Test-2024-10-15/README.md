Test report

**note**: Already cloned this wot-py repository.

Run docker build (Figure 1) and get image ID

### Commands

```sh
cd wot-py
docker build .
```


Image ID is e5d22008c11c - from `docker images` command (Figure 2)

Next command is `docker container run --network host -it --rm --user 1000:1000 -v $PWD/examples/uv_sensor:/app e5d22008c11c sh` - It opens a shell prompt to start the **server**.

Start the **server**: `python server.py`

### device wiring

Component list:
| aaa | bbb | ccc |
| --- | --- | --- |
| 1 | ESP32S dev kit | --- |
| 1 | 1k$\Omega$ resistor  | name one lead as A, other as B |
| 1 | LDR  | name one lead as A, other as B |
| 1 | OLED display  | for future use. Information on how to use it in https://github.com/FNakano/CFA/tree/master/projetos/py-OLED |

component wiring (necessary)
| 1k resistor lead | LDR lead | Pino do ESP32 |
| --- | --- | --- |
| A | - | GND |
| B | B | 34 |
| - | A | 3V3 |

component wiring (for future use)
| display Pin | Pino do ESP32 |
| --- | --- |
| SCL ou SCK | 18 |
| SDA | 19 |
| GND | GND |
| VCC | VCC |

### device programs

[main.py](./main.py): Connects ESP32S **Dev Kit** to a WiFi Access Point. Modify line maked with `# write your network credentials here` and restart (CTRL-D) the dev kit.

[analogLight.py](./analogLight.py): This program executes a web client on an ESP32S Dev Kit with Micropyton 1.23.0 . Copy the program into the **Dev Kit**, in

```python
# Thing Descriptions
TD = {
    'uv_sensor': {"links": [{"href": "http://192.168.0.9:9494/urn:esp32/property/uv"}]},
    # Add sensors as needed
}

```

overwrite `192.168.0.9` with you **server** IP address, save file, import package and run its `main` function.

```python
import analogLight
analogLight.main()

```

### integration tests

With the **server** and the **Dev Kit** programs running, at 5s interval **Dev Kit** sends a HTTP PUT request with a JSON payload to store a light intensity measurement into the server.

Example of payload sent in HTTP PUT by **Dev Kit**
```json
{
    'uv_sensor': ['type': 'uv', 'sensor': 777]
}
```

The server repacks the measurement as RDF triples:

Example of one measurement packed in RDF
```rdf
@prefix ns1: <http://www.w3.org/ns/sosa/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<http://wotpyrdfsetup.org/device/Observation20231120005521408626> a ns1:Observation ;
    ns1:hasResult "777"^^<http://wotpyrdfsetup.org/device/UVValue> ;
    ns1:resultTime "2023-11-20T00:55:21.409298"^^xsd:dateTime .

```

**Dev Kit** prints messages to REPL console (Figure 3)

**server** prints messages to terminal (Figure 4)

### SPARQL endpoint and query

A SPARQL endpoint can be browsed in http://localhost:9595/query

A SPARQL query can be written in the text box and executed.

```
prefix sosa: <http://www.w3.org/ns/sosa/>
select * where {?s sosa:hasResult ?o}

```

resulting in (after a JSON beautifier)

```
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


```


### Results

Figure 1 - `docker build .` warning example:
  
![](./Captura%20de%20tela%20de%202024-10-14%2016-28-42.png)

Figure 2 - `docker images` screenshot:

![](./Captura%20de%20tela%20de%202024-10-14%2014-03-44.png)

Figure 3 - **Dev Kit** REPL

![](./Captura%20de%20tela%20de%202024-10-14%2016-23-00.png)

Figure 4 - server messages after some insertions and SPARQL query

![](./Captura%20de%20tela%20de%202024-10-14%2016-27-53.png)

### Comments

Some warnings on not using `venv` (version changes are system-wide and may affect other applications).

