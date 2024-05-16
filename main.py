import umqtt.simple as mqtt

from machine import Pin
from time import sleep

import dht

# MQTT inställningar
MQTT_BROKER = '185.189.49.210'
MQTT_PORT = 1883
MQTT_TOPIC = 'test/iot'
MQTT_USERNAME = 'iot_project'
MQTT_PASSWORD = '800grader'

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
    sleep(2)
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
  