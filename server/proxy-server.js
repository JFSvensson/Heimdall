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

mqttClient.on('connect', () => {
  console.log('Connected to MQTT broker');
  mqttClient.subscribe('test/iot', (err) => {
    if (err) {
      console.error('Failed to subscribe to topic', err);
    }
  });
});

mqttClient.on('message', (topic, message) => {
  console.log('Received message:', topic, message.toString());
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message.toString());
    }
  });
});

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
