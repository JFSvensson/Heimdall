import umqtt.simple as mqtt
from machine import Pin
import json
import network
import time
import dht
import uasyncio as asyncio
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
MQTT_LED_STATUS_TOPIC = 'test/iot/led_status'

# Initiera MQTT klient
client = mqtt.MQTTClient('client_id', MQTT_BROKER, port=MQTT_PORT, user=MQTT_USERNAME, password=MQTT_PASSWORD)

# Anslut till MQTT broker
client.connect()

ledPin = Pin("LED", Pin.OUT)
sensor = dht.DHT22(Pin(22))

async def handle_message(topic, msg):
    try:
        data = json.loads(msg)
        if data.get('action') == 'toggle_led':
            ledPin.value(not ledPin.value())
            # Skicka LED-status till MQTT broker
            led_status = 'on' if ledPin.value() else 'off'
            client.publish(MQTT_LED_STATUS_TOPIC, json.dumps({'led_status': led_status}))
    except Exception as e:
        print('Failed to handle message:', e)

def mqtt_callback(topic, msg):
    loop = asyncio.get_event_loop()
    loop.create_task(handle_message(topic, msg))

client.set_callback(mqtt_callback)
client.subscribe(MQTT_TOPIC)

async def read_sensor():
  while True:
    try:
      sensor.measure()
      temp = sensor.temperature()
      hum = sensor.humidity()

      data = {
              'temperature': temp,
              'humidity': hum
          }
      # Skicka data till MQTT broker
      client.publish(MQTT_TOPIC, json.dumps(data))
      print('Published:', data)

    except OSError as e:
      print('Failed to read sensor.')
    except Exception as e:
      print('An error occurred:', e)
    await asyncio.sleep(2)
  
async def main():
    asyncio.create_task(read_sensor())
    while True:
        client.check_msg()
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
