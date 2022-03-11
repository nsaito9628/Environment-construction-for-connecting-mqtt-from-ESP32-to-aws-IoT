import utime
import json
from umqtt.robust import MQTTClient

import uos
import machine

CERT_FILE = "your cert.der PATH"
KEY_FILE = "your key.der PATH"
MQTT_CLIENT_ID = "your aws IoT thing name"
MQTT_PORT = 8883
MQTT_TOPIC = "$aws/things/%s/shadow/" %MQTT_CLIENT_ID

MQTT_HOST = "your AWS IoT endpoint"
mqtt_client = None

ssid='your NW AP SSID'
pw = 'your NW AP password'


def connect_wifi(ssid, pw):
    from network import WLAN
    from network import STA_IF
    import machine

    wlan = WLAN(STA_IF)
    wlan.active(True)
    nets = wlan.scan()
    if(wlan.isconnected()):
        wlan.disconnect()            
    wlan.connect(ssid, pw)         
    while not wlan.isconnected():             
        machine.idle() # save power while waiting
        print('WLAN connection succeeded!')         
        break 
    print("connected:", wlan.ifconfig())

def pub_msg(msg):
    global mqtt_client
    try:    
        mqtt_client.publish(MQTT_TOPIC, msg)
        print("Sent: " + msg)
    except Exception as e:
        print("Exception publish: " + str(e))
        raise
    
def connect_mqtt():    
    global mqtt_client

    try:
        with open(KEY_FILE, "r") as f: 
            key = f.read()
        print("Got Key")
            
        with open(CERT_FILE, "r") as f: 
            cert = f.read()
        print("Got Cert")

        mqtt_client = MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_HOST, port=MQTT_PORT, keepalive=5000, ssl=True, ssl_params={"cert":cert, "key":key, "server_side":False})
        mqtt_client.connect()
        print('MQTT Connected')

        ## Send telemetry
        #for i in range(0, 10):
        while True:
            msg = json.dumps({"message": "Hello Pico!!"})
            pub_msg(msg)
            utime.sleep(3)

        mqtt_client.disconnect()
        
    except Exception as e:
        print('MQTT Exception : ' + str(e))
        raise
