# Environment-construction-for-connecting-mqtt-from-ESP32-to-aws-IoT
Build an environment for connecting ESP32 DevKit to a wifi access point with MicroPython and MQTT connection to aws IoT  



## **Construction procedure**  

### **Erase and write flash ESP32**
.  


Binaryization of certificates and private keys
```sh  

openssl x509 -in your_cert.pem -outform DER -out cert.der  
openssl rsa -in your_secretkey.pem -outform DER -out key.der

```


Clone this project from public repository
```sh  

git clone https://

cp 

cd ./esptool-master

esptool.py --chip esp32 --port /dev/ttyUSB10 erase_flash  

esptool.py --chip esp32 --port /dev/ttyUSB10 --baud 460800 write_flash -z 0x1000 esp32-20220117-v1.18.bin


```
  
