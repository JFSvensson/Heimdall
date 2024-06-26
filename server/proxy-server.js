const mqtt = require('mqtt');
const WebSocket = require('ws');
const express = require('express');
const http = require('http');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const mqttClient = mqtt.connect('mqtt://185.189.49.210:1883', {
  username: 'iot_project',
  password: '800grader'
});

const ADAFRUIT_IO_WEBHOOK_TEMPERATURE = SECRET_URL;
const ADAFRUIT_IO_WEBHOOK_HUMIDITY = SECRET_URL;
const ADAFRUIT_IO_WEBHOOK_LED_STATUS = SECRET_URL;
const ADAFRUIT_IO_KEY = SECRET_KEY;

mqttClient.on('connect', () => {
  console.log('Connected to MQTT broker');
  mqttClient.subscribe('test/iot', (err) => {
    if (err) {
      console.error('Failed to subscribe to topic', err);
    }
  });
  mqttClient.subscribe('test/iot/led_status', (err) => {
    if (err) {
      console.error('Failed to subscribe to LED status topic', err);
    }
  });
});

let buffer = [];
const BUFFER_LIMIT = 10; 
const SEND_INTERVAL = 60 * 1000;

mqttClient.on('message', (topic, message) => {
  console.log('Received message:', topic, message.toString());
  
  if (topic === 'test/iot') {
    const data = JSON.parse(message.toString());
    buffer.push(data);

    if (buffer.length >= BUFFER_LIMIT) {
      sendDataToAdafruit(buffer);
      buffer = [];
    }
  }

  if (topic === 'test/iot/led_status') {
    const data = JSON.parse(message.toString());
    sendLedStatusToAdafruit(data);
  }

  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message.toString());
    }
  });
});

setInterval(() => {
  if (buffer.length > 0) {
    sendDataToAdafruit(buffer);
    buffer = [];
  }
}, SEND_INTERVAL);

function sendDataToAdafruit(buffer) {
  const avgTemp = buffer.reduce((sum, data) => sum + data.temperature, 0) / buffer.length;
  const avgHum = buffer.reduce((sum, data) => sum + data.humidity, 0) / buffer.length;

  fetch(ADAFRUIT_IO_WEBHOOK_TEMPERATURE, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'X-AIO-Key': ADAFRUIT_IO_KEY
    },
    body: JSON.stringify({ value: avgTemp })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    console.log('Temperature data sent to Adafruit IO');
  })
  .catch(error => {
    console.error('Error sending temperature data to Adafruit IO:', error);
  });

  fetch(ADAFRUIT_IO_WEBHOOK_HUMIDITY, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'X-AIO-Key': ADAFRUIT_IO_KEY
    },
    body: JSON.stringify({ value: avgHum })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    console.log('Humidity data sent to Adafruit IO');
  })
  .catch(error => {
    console.error('Error sending humidity data to Adafruit IO:', error);
  });
}

function sendLedStatusToAdafruit(data) {
  fetch(ADAFRUIT_IO_WEBHOOK_LED_STATUS, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'X-AIO-Key': ADAFRUIT_IO_KEY
    },
    body: JSON.stringify({ value: data.led_status })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    console.log('LED status sent to Adafruit IO');
  })
  .catch(error => {
    console.error('Error sending LED status to Adafruit IO:', error);
  });

  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({ led_status: data.led_status })); 
    }
  });
}

wss.on('connection', (ws) => {
  console.log('WebSocket client connected');
  
  ws.on('message', (message) => {
    console.log('Received message from WebSocket client:', message);
    // Forward the message to the MQTT broker
    mqttClient.publish('test/iot', message);
  });

  ws.on('close', () => {
    console.log('WebSocket client disconnected');
  });
});

server.listen(3000, () => {
  console.log('Server is listening on port 3000');
});
