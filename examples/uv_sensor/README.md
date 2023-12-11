# UV Sensor Data Transmission with ESP32 and WoT with RDF Integration

This project demonstrates transmitting UV sensor data from an ESP32 microcontroller to a Web of Things (WoT) server via the HTTP protocol, with added functionality of RDF graph integration and SPARQL endpoint for advanced data querying. The project utilizes the WotPy library for server creation and WoT interactions, the ESP32 microcontroller paired with an ML8511 UV sensor, and RDFLib with BerkeleyDB for managing RDF graphs.

Two main code files comprise this project: server.py and main.py. The server.py sets up the WoT server, exposes a Thing representing the UV sensor, and defines custom handlers for reading and writing UV sensor data. The main.py, running on the ESP32, periodically reads UV sensor data and sends it to the WoT server using HTTP requests.

To utilize this project, run the server.py file on your Python server and load the main.py file onto your ESP32. The ESP32 will continuously read UV sensor data and transmit it to the server, where it can be accessed and observed through the exposed Thing.

This project serves as a foundational example of integrating IoT devices with WoT principles, facilitating seamless communication and interoperability between devices and applications within a decentralized IoT ecosystem.

Feel free to customize and expand upon this project to suit your specific requirements and sensor configurations.

## Key Components

- **WoTPy Server with RDF Graph Integration:** The `server.py` sets up the WoT server and integrates RDF graphs using RDFLib and BerkeleyDB for storing data.
- **SPARQL Endpoint for Advanced Data Querying:** Implementation of a SPARQL endpoint using Tornado web framework, allowing complex data querying.
- **UV Sensor Data Processing:** The `main.py`, running on the ESP32, periodically reads UV sensor data and sends it to the WoT server using HTTP requests.

## Environment Setup

### WoT Server

This document assumes you have docker installed on your machine. If not, please visit the [official website](https://docs.docker.com/get-docker/) to install it.

First, execute the following commands in your terminal:
```sh
git clone https://github.com/T16K/wot-py.git
cd wot-py
docker build .
```

Now you've built an image from the Dockerfile. Next, check the IMAGE ID:
```sh
docker images
```

Copy the characters in the IMAGE ID column and replace `IMAGE_ID` and `USER`  in the following command:
```sh
docker container run --network host -it --rm --user 1000:1000 -v $PWD/examples/uv_sensor:/app 'IMAGE_ID' sh
```

We are now running a Docker container using the specified image with the host network stack, which provides interactive access to a shell session, and mounting the current working directory to the /app directory inside the container.

Finally, access the server.py file, and we have the server running:
```sh
cd examples/uv_sensor
python server.py
```

This initiates the WoT server with RDF graph integration and starts the SPARQL endpoint on a specified port.

### ESP32

For detailed information, see this [document](https://t16k-ach2157.readthedocs.io/en/latest/comp/esp.html) in Portuguese.

## File Explanations

### server.py

1. Import Statements

The script imports necessary libraries and modules. `json` for JSON parsing, `logging` for logging messages, and `tornado` modules for web server functionalities. The `wotpy` modules are used for setting up the WoT server, and `rdflib` modules for RDF graph operations.
```py
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
from datetime import datetime```
```

2. Global Variables:
```py
HTTP_PORT = 9494
SPARQL_PORT = 8585
ID_THING = "urn:esp32"
UV_SENSOR = "uv"

uv_data = None
```

- `HTTP_PORT` and `SPARQL_PORT` define the ports for the HTTP and SPARQL servers, respectively.
- `ID_THING` and `UV_SENSOR` are identifiers for the WoT Thing and the UV sensor property.
- `uv_data` is initialized to store the UV sensor data.

3. Setting up [logging](https://docs.python.org/3/library/logging.html):
```py
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
```
Basic logging is configured, and the logger's level is set to `INFO`.

4. RDF Graph Store Initialization
```py
config = "berkeley_db"
store = berkeleydb.BerkeleyDB(configuration=config)
g = Graph(store=store, identifier=ID_THING)
g.open(config, create=True)
```

- `config` sets the configuration for the BerkeleyDB store.
- `store` initializes the BerkeleyDB store.
- `g` creates an RDF graph with BerkeleyDB as the store and the Thing ID as the identifier.
- Namespaces `ssn`, `sosa`, and `ex` are defined for use in the graph.

5. [WoT Thing Description](https://www.w3.org/TR/wot-thing-description/):
```py
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
```

This dictionary represents the Thing description. It specifies the Thing's ID, name, and properties. In this case, it defines the `UV_SENSOR` property as a number type that can be read and observed.

6. SPARQL Endpoint Handlers:
```py
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
```

- `SPARQLHandler`: Handles direct SPARQL query requests via POST method, executing queries on the RDF graph and returning results in JSON format.
- `SparqlQueryHandler`: Manages the web interface for SPARQL queries, allowing users to input queries via a form and view results on a web page.

7. SPARQL Server Initialization:
```py
class SPARQLServer(Application):
    def __init__(self):
        handlers = [
            ("/sparql", SPARQLHandler),
            ("/query", SparqlQueryHandler)
        ]
        super(SPARQLServer, self).__init__(handlers)
```

A Tornado web application configured with URL routes to handle SPARQL queries through the defined handlers. It routes `/sparql` for direct queries and `/query` for the web interface.

8. Custom HTTP WoT Server
```py
class CustomHTTPServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        super(CustomHTTPServer, self).__init__(*args, **kwargs)
```
Extends WotPy's `HTTPServer` class to set up a custom HTTP server for the WoT (Web of Things) functionalities, enabling the exposure of IoT devices as WoT "Things."

9. UV Data Reading/Writing Functions
```py
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
```
These coroutine functions are designed for asynchronous reading and writing of UV sensor data. `write_uv` also updates the RDF graph with new sensor observations.

10. Server Start Functions
```py
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
```
- `start_server`: Initializes the WoT server with the custom HTTP server.
- `start_sparql_server`: Starts the SPARQL server for processing RDF graph queries.

### main.py

- Importing the necessary modules:
```py
import machine
import ujson
import urequests
import time
```

- Sensor setup:
```py
sensors = {
    'uv_sensor': {'type': 'uv', 'sensor': machine.ADC(machine.Pin(34))},
    # Add sensors as needed
}
```
This dictionary contains the sensor configurations. In this case, it defines an uv_sensor with its type as 'uv' and specifies the corresponding pin on the ESP32.

`machine.ADC`: This class is part of the MicroPython machine module and is used to configure and read values from an Analog-to-Digital Converter (ADC) channel. You can refer to the [MicroPython machine.ADC documentation](https://docs.micropython.org/en/latest/library/machine.ADC.html) for more details.

`machine.Pin`: This class is part of the MicroPython machine module and is used to configure and control GPIO pins. You can refer to the [MicroPython machine.Pin documentation](https://docs.micropython.org/en/latest/library/machine.Pin.html) for more details.

- Thing Description:
```py
TD = {
    'uv_sensor': {"links": [{"href": "http://000.000.0.00:9494/urn:esp32/property/uv"}]},
    # Add sensors as needed
}
```
The TD dictionary holds the descriptions of the Things. It contains a link to the UV sensor property on the server.

- Function to send sensor data to the server:
```py
def send_sensor_data(sensor_id, sensor_type, url, data):
    headers = {'content-type': 'application/json'}
    try:
        r = urequests.put(url.format(sensor_id), data=ujson.dumps(data), headers=headers)
        if r.status_code >= 200 and r.status_code < 300:
            print('Successfully sent {} data from {} to WoT server'.format(sensor_type, sensor_id))
        else:
            print('Failed to send {} data from {} to WoT server: received status code {}'.format(sensor_type, sensor_id, r.status_code))
        r.close()
    except Exception as e:
        print('Could not send {} data from {} to WoT server: '.format(sensor_type, sensor_id), e)
```
This function takes the sensor ID, type, URL, and data as input. It sends an HTTP PUT request to the server with the data payload in JSON format. It then prints a success or failure message based on the response status code.

`ujson.dumps`: This function is provided by the MicroPython ujson module and is used to serialize a Python object into a JSON-formatted string. You can refer to the [MicroPython ujson documentation](https://docs.micropython.org/en/latest/library/json.html) for more details.

`urequests.put`: This function is provided by the MicroPython urequests module and is used to send an HTTP PUT request. It is similar to the requests library in Python. You can refer to the [MicroPython urequests documentation](https://makeblock-micropython-api.readthedocs.io/en/latest/public_library/Third-party-libraries/urequests.html) for more details.

- Main function:
```
def main():
    while True:
        for sensor_id, sensor_info in sensors.items():
            sensor_value = sensor_info['sensor'].read()
            data = {sensor_info['type']: sensor_value}
            url = TD[sensor_id]['links'][0]['href']
            send_sensor_data(sensor_id, sensor_info['type'], url, data)
        time.sleep(5)

if __name__ == "__main__":
    main()
```

The main function is executed when the script is run. It enters an infinite loop and iterates through each sensor defined in the sensors dictionary. It reads the sensor value, creates a data object with the corresponding type, retrieves the URL from the Thing Description (TD), and calls the send_sensor_data function to send the data to the server. The loop waits for 5 seconds before repeating.

`time.sleep`: This function is part of the Python time module and is used to pause the execution of the program for a specified number of seconds. You can refer to the [Python time documentation](https://docs.python.org/3/library/time.html#time.sleep) for more details.

### boot.py

The boot.py file is a script that runs automatically when the ESP32 starts up. Its purpose is to [establish a Wi-Fi connection](https://docs.micropython.org/en/latest/esp32/quickref.html#networking) to the specified network, allowing the ESP32 to connect to the internet and communicate with the WoT server.

The code defines a function called `do_connect` that takes the SSID (network name) and password as arguments. Within the function, it imports the network module to manage the Wi-Fi connection.

The function checks if the ESP32 is already connected to a network using the `isconnected` method of the `STA_IF` interface (station interface). If the ESP32 is not connected, it proceeds to connect by activating the station interface `(active(True))` and calling the connect method with the provided SSID and password.

After initiating the connection, the code enters a loop that waits until the ESP32 successfully connects to the network (isconnected() returns True).

Once the connection is established, it prints the network configuration details (IP address, subnet mask, gateway, etc.) using the ifconfig method of the station interface.

To use this script, replace 'YourSSID' with the SSID of your Wi-Fi network and 'YourPassword' with the corresponding password.

By including this boot.py script on your ESP32, it will automatically connect to the specified Wi-Fi network upon startup, ensuring a reliable internet connection for your application.

Remember to upload the modified boot.py file to the ESP32 and verify that the network credentials are correct before deploying your project.

## Example (HTTP side)

Both ESP32-based device and web browser communicate to WotPy servient through port 9494.

Notice that ESP32-based device only sends information. It makes PUT requests to the servient (the request type is defined in WoT recommendation and implemented into WotPy). Also, the browser only receives information. It makes GET requests to the server (browse http://localhost:9494/urn:esp32/property/uv).

Figure 1: O dispositivo (ESP32) executa um loop que, a cada 5 segundos executa a função send\_sensor\_data. Esta função envia uma requisição PUT para o servidor (WoTPy). Em resposta a essa requisição o servidor executa o handler (função) write\_uv que contém o envio da resposta. Um usuário pode acessar a informação no servidor através do Browser. Entrar a URL na barra de endereços do Browser o faz enviar ao servidor uma requisição GET. Em resposta à requisição o servidor executa o handler (função) read\_uv, que contém o envio da resposta - no caso, o valor de uv mais recente. O Browser recebe essa informação e renderiza a página contendo a informação.

![Figure1](sequencia.png)

One can send data (simulate am ESP32-based device sending data) with cURL command: `curl -X PUT -H "Content-Type: application/json" -d '{"uv":"31"}' http://localhost:9494/urn:esp32/property/uv`


## Example (SPARQL side)

Access the SPARQL query page at http://localhost:8585/query to perform complex queries on the RDF graph containing UV sensor data.

Example SPARQL Query:
```
SELECT * WHERE {?s ?p ?o}
```

This query retrieves all triples in the RDF graph.
