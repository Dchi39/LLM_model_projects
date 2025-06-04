#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

// Wi-Fi credentials
const char* ssid = "";       // Replace with your Wi-Fi SSID
const char* password = "";        // Replace with your Wi-Fi password

// Relay pins
#define WHITE_RELAY 26
#define YELLOW_RELAY 33

// Servo pin
#define SERVO_PIN 25

// Create web server and servo object
WebServer server(80);
Servo myServo;

void handleCommand();

void setup() {
  Serial.begin(115200);

  // Initialize relay pins
  pinMode(WHITE_RELAY, OUTPUT);
  pinMode(YELLOW_RELAY, OUTPUT);

  // Set relays initially OFF
  digitalWrite(WHITE_RELAY, HIGH);
  digitalWrite(YELLOW_RELAY, HIGH);
  delay(3000);
  digitalWrite(WHITE_RELAY, LOW);
  digitalWrite(YELLOW_RELAY, LOW);
  delay(1000);

  // Attach and center the servo
  myServo.attach(SERVO_PIN);
  myServo.write(90);  // Center position

  // Connect to Wi-Fi
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected! IP Address:");
  Serial.println(WiFi.localIP());

  // Define command handler
  server.on("/command", handleCommand);
  server.begin();
  Serial.println("Server started.");
}

void loop() {
  server.handleClient();
}

void handleCommand() {
  if (!server.hasArg("cmd")) {
    server.send(400, "text/plain", "Missing command");
    return;
  }

  String cmd = server.arg("cmd");
  cmd.trim();
  Serial.println("Received command: " + cmd);

  if (cmd == "W_ON") {
    digitalWrite(WHITE_RELAY, HIGH);
  } else if (cmd == "W_OFF") {
    digitalWrite(WHITE_RELAY, LOW);
  } else if (cmd == "Y_ON") {
    digitalWrite(YELLOW_RELAY, HIGH);
  } else if (cmd == "Y_OFF") {
    digitalWrite(YELLOW_RELAY, LOW);
  } else if (cmd == "SERVO_LEFT") {
    myServo.write(0);
  } else if (cmd == "SERVO_RIGHT") {
    myServo.write(180);
  } else if (cmd == "SERVO_CENTER") {
    myServo.write(90);
  } else {
    server.send(400, "text/plain", "Unknown command");
    return;
  }

  server.send(200, "text/plain", "OK");
}