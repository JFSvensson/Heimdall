from machine import Pin
from time import sleep

import dht

# pin = Pin("LED", Pin.OUT)
# while True:
#   pin.toggle()
#   sleep(1)

sensor = dht.DHT22(Pin(22))

while True:
  try:
    sensor.measure()
    sleep(2)
    temp = sensor.temperature()
    hum = sensor.humidity()

    print('Temperature: C', temp)

    print('Humidity:', hum)
  except OSError as e:
    print('Failed to read sensor.')
    break
  except Exception as e:
    print('An error occurred:', e)
  