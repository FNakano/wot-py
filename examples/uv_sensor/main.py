import machine
import ujson
import urequests

# Assume ML8511 is connected to pin 34
adc = machine.ADC(machine.Pin(34))

TD = {
    "links": [
        {"href": "http://192.168.162.111:8080/uv"}
    ]
}

while True:
    uv_value = adc.read()  # Replace with your function to read UV value from ML8511
    data = {"uv": uv_value}
    url = TD['links'][0]['href']  # Assuming only one link is specified
    headers = {'content-type': 'application/json'}
    
    try:
        r = urequests.post(url, data=ujson.dumps(data), headers=headers)
        r.close()
    except Exception as e:
        print('Could not send data to WoT server: ', e)

    # sleep for some time before sending the next value
    machine.sleep(1000)  # Sleep for 1 seconds
