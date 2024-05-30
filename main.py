import umqtt.simple as mqtt
from machine import Pin
import network
import time
import dht
from credentials import WIFI_SSID, WIFI_PASSWORD, MQTT_USERNAME, MQTT_PASSWORD

# Anslut till WiFi-nätverk
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

max_attempts = 10
attempt = 0

while attempt < max_attempts and not wlan.isconnected():
    print('Connecting to network...')
    time.sleep(1)
    attempt += 1

if wlan.isconnected():
    print('Network connected!')
    print('IP address:', wlan.ifconfig()[0])
else:
    print('Failed to connect to network')

# MQTT inställningar
MQTT_BROKER = '185.189.49.210'
MQTT_PORT = 1883
MQTT_TOPIC = 'test/iot'

# Initiera MQTT klient
client = mqtt.MQTTClient('client_id', MQTT_BROKER, port=MQTT_PORT, user=MQTT_USERNAME, password=MQTT_PASSWORD)

# Anslut till MQTT broker
client.connect()

ledPin = Pin("LED", Pin.OUT)
sensor = dht.DHT22(Pin(22))

while True:
  try:
    sensor.measure()
    ledPin.toggle()
    time.sleep(2)
    temp = sensor.temperature()
    hum = sensor.humidity()

    data = {
            'temperature': temp,
            'humidity': hum
        }
    # Skicka data till MQTT broker
    client.publish(MQTT_TOPIC, str(data))

    print('Published:', data)
    # print('Temperature: C', temp)
    # print('Humidity:', hum)

  except OSError as e:
    print('Failed to read sensor.')
    break
  except Exception as e:
    print('An error occurred:', e)
  