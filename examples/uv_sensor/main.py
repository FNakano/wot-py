import machine
import ujson
import urequests
import time

adc = machine.ADC(machine.Pin(34))

TD = {
    "links": [
        {"href": "http://000.000.0.000:0000"}
    ]
}

while True:
    uv_value = adc.read()
    data = {"uv": uv_value}
    url = TD['links'][0]['href']
    headers = {'content-type': 'application/json'}

    try:
        r = urequests.post(url, data=ujson.dumps(data), headers=headers)
        if r.status_code >= 200 and r.status_code < 300:
            print('Successfully sent data to WoT server')
        else:
            print('Failed to send data to WoT server: received status code {}'.format(r.status_code))
        r.close()
    except Exception as e:
        print('Could not send data to WoT server: ', e)

    time.sleep(10)
