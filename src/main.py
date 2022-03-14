import sys
import utime
import json
from umqtt.robust import MQTTClient
import uos
#import machine
from machine import Pin


#####################################################################
#parameters of ESP32 signal dashboard system 
#####################################################################
HOST = "your AWS IoT endpoint"
PORT = 8883  # mqtts port

CLIENTCERT = "your cert.der PATH"
CLIENTKEY = "your key.der PATH"
MQTT_CLIENT_ID = "your aws IoT thing name"
TOPIC = "$aws/things/%s/shadow/" %MQTT_CLIENT_ID

SSID_AP = 'your NW AP SSID'
PW_AP = 'your NW AP password'

MOTION_PIN = 17 #GPIO port No.
#####################################################################


class Com:
    def __init__(self):
        self.mqtt_client = None
        self.clientCert = CLIENTCERT
        self.clientKey = CLIENTKEY
        self.client_id = MQTT_CLIENT_ID
        self.host = HOST
        self.port = PORT
        self.topic = TOPIC
        self.ssid = SSID_AP
        self.pw = PW_AP
    
    #Callback function when mqtt connection is successful
    def connect_wifi(self):
        from network import WLAN
        from network import STA_IF
        import machine

        wlan = WLAN(STA_IF)
        wlan.active(True)
        nets = wlan.scan()
        if(wlan.isconnected()):
            wlan.disconnect()            
        wlan.connect(self.ssid, self.pw)            
        while not wlan.isconnected():             
            machine.idle() # save power while waiting
            print('WLAN connection succeeded!')         
            break 
        print("connected:", wlan.ifconfig())

    def connect_mqtt(self):

        try:
            with open(self.clientKey, "r") as f: 
                key = f.read()
            print("Got Key")
                
            with open(self.clientCert, "r") as f: 
                cert = f.read()
            print("Got Cert")

            self.mqtt_client = MQTTClient(client_id=self.client_id, server=self.host, port=self.port, keepalive=5000, ssl=True, ssl_params={"cert":cert, "key":key, "server_side":False})
            self.mqtt_client.connect()
            print('MQTT Connected')
            
        except Exception as e:
            print('MQTT Exception : ' + str(e))
            raise

    #Function that dispenses motion sensor data to the cloud at 0 seconds per minute
    def publish(self, motion_count):

        body = json.dumps({"motion_detect": motion_count})
        try:    
            self.mqtt_client.publish(self.topic, body)
            print("Sent: " + body)
        except Exception as e:
            print("Exception publish: " + str(e))
            raise


class Sensor:
    def __init__(self):
        self.motion_pin = MOTION_PIN 
        self.pir = Pin(MOTION_PIN, Pin.IN)
    
    #Output sensor HI / LO at 1/0
    def motion_detect(self):
        sig = 0
        if self.pir.value() == 0:
            sig = 0
        else:
            print("Hello Nyanko!")
            sig = 1
        
        return sig

    def motion_count(self, motion_count):
        
        motion_sig = self.motion_detect()
        
        if motion_sig == 1:
            motion_count = motion_count + 1

        return motion_count


class Loop:
    senser = Sensor()
    com = Com()
    def __init__(self):
        return
        
    def get_start(self):
        while True:
            if (utime.localtime()[4] == 0 or utime.localtime()[4] == 10 or utime.localtime()[4] == 29 or utime.localtime()[4] == 30 or utime.localtime()[4] == 40 or utime.localtime()[4] == 50) and utime.localtime()[5] == 0:
                print("start")
                break
        return

    def loop(self):
        t0 = utime.ticks_ms()
        td = 0
        motion_count = 0

        while True:
            td = utime.ticks_ms() - t0
            motion_count = senser.motion_count(motion_count)

            if td > 60000:
                com.publish(motion_count)
                t0 = utime.ticks_ms()
                td = 0
                motion_count = 0

            utime.sleep(0.2)


if __name__ == '__main__':
    senser = Sensor()
    com = Com()
    loop = Loop()
    try:
        #wifi connection confirmation and MQTT connection
        com.connect_wifi()
        utime.sleep(10)
        com.connect_mqtt()

        #Main loop execution
        loop.get_start()
        loop.loop()

    except KeyboardInterrupt:
        sys.exit()
