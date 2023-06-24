# UV Sensor Data Transmission with ESP32 and WoT

This project aims to demonstrate the transmission of UV sensor data from an ESP32 microcontroller to a Web of Things (WoT) server using the HTTP protocol. The project utilizes the WotPy library for creating the server and handling WoT interactions, as well as the ESP32 microcontroller with the ML8511 UV sensor.

The code consists of two main files: server.py and main.py. The server.py file sets up the WoT server, exposes a Thing representing the UV sensor, and defines custom handlers for reading and writing the UV sensor data. On the other hand, the main.py file runs on the ESP32 and reads the UV sensor data periodically, sending it to the WoT server using HTTP requests.

To use this project, you need to run the server.py file on your Python server and load the main.py file onto your ESP32. The ESP32 will continuously read the UV sensor data and send it to the server, where it can be accessed and observed through the exposed Thing.

This project serves as a basic example of integrating IoT devices with WoT principles, enabling seamless communication and interoperability between devices and applications in a decentralized IoT ecosystem.

Feel free to customize and expand upon this project to suit your specific requirements and sensor configurations.

## server.py

- Importing the necessary libraries and modules:
```py
import json
import logging
import tornado.gen
from tornado.ioloop import IOLoop
from wotpy.protocols.http.server import HTTPServer
from wotpy.wot.servient import Servient
```

- Defining constants:
```py
HTTP_PORT = 9494
ID_THING = "urn:esp32"
UV_SENSOR = "uv"
```
The HTTP_PORT constant specifies the port on which the server will listen. ID_THING represents the identifier for the Thing, and UV_SENSOR is the name of the property representing the UV sensor.

- Global data storage:
```py
uv_data = None
```
This variable will store the latest UV sensor data received from the ESP32.

- Setting up logging:
```py
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
```
Configuring the logger to display log messages with the level set to INFO.

- Thing description:
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
This dictionary represents the Thing description. It specifies the Thing's ID, name, and properties. In this case, it defines the UV_SENSOR property as a number type that can be read and observed.

- Custom handlers for reading and writing UV data:
```py
@tornado.gen.coroutine
def read_uv():
    """Custom handler for the 'UV' property."""
    if uv_data is None:
        return
    uv_data_dict = json.loads(uv_data.decode("utf-8"))
    return float(uv_data_dict['uv'])

@tornado.gen.coroutine
def write_uv(value):
    """Custom handler for writing UV data."""
    global uv_data
    uv_data = value
```
These two functions serve as custom handlers for reading and writing the UV sensor data. The read_uv function parses the stored UV data and returns it as a float. The write_uv function updates the uv_data variable with the received value.

- Starting the server:
```py
@tornado.gen.coroutine
def start_server():
    http_server = HTTPServer(port=HTTP_PORT)
    servient = Servient()
    servient.add_server(http_server)
    wot = yield servient.start()
    exposed_thing = wot.produce(json.dumps(description))
    exposed_thing.set_property_read_handler(UV_SENSOR, read_uv)
    exposed_thing.set_property_write_handler(UV_SENSOR, write_uv)
    exposed_thing.expose()

if __name__ == "__main__":
    IOLoop.current().add_callback(start_server)
    IOLoop.current().start()
```
The start_server function creates an HTTP server using the specified port and initializes the WotPy Servient. It then starts the servient, produces the Thing based on the description, sets the custom read and write handlers for the UV property, and exposes the Thing. Finally, the server is started by adding the start_server function to the IOLoop.
