import network
network.hostname("nak1")
wifi_if=network.WLAN(network.STA_IF)
wifi_if.active(True) 
wifi_if.connect('your wifi', 'your wifi password') # write your network credentials here

import time
t=0
while (not(wifi_if.isconnected()) and (t<10)):
    print('Trying to connect to AP...')
    sleep_ms(500) # one time is 500ms
    t=t+1  # wait at most 10 times

if (t<10) :
    print(wifi_if.ifconfig()) # print IP
else:
    print ("Not connected to AP.")
