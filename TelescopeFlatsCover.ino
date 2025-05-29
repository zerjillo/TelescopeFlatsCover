/*
This program is free software: you can redistribute it and/or modify it under the 
terms of the GNU General Public License as published by the Free Software 
Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or 
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>. 

(C) Copyright 2025, Sergio Alonso and Javier Flores
*/
#include <CommandParser.h>
#include <Servo.h>

const char VERSION[] = "1.00b";
const int TEMP_SENSOR = A0;
const int OPTO_PIN = 7;
const int SERVO_PIN = 9;
const int CLOSED_ANGLE = 0;
const int OPENED_ANGLE = 90;

bool coverOpen = false;  // Is the cover open?
bool lightOn = false;    // Is the light on?
bool printStatusPeriodically = false;  // Should it print periodic STATUS messages?
int updateInterval = 10; // In seconds
long lastUpdate = 0;     // To save the last time and status message was sent

Servo servo;             // To control the servo motor
typedef CommandParser<> MyCommandParser;  // To parse commands
MyCommandParser parser;

// Gets the temperature readed by the TMP36 sensor
float getTemperature() {
  int read = analogRead(TEMP_SENSOR);
  float temperature = (read * (500.0 / 1023.0)) - 50.0;  // In Celsius degrees
  return temperature; 
}

// Prints the status of the device: "STATUS coverOpen lightOn temperature printStatusPeriodically updateInterval"
// For example: "STATUS 0 1 24.3 1 15" means:
// The cover is closed, the light is ON, the sensor reads 24.3 ºC, and the device is sending STATUS messages every 15 seconds.
void printStatus() {
  Serial.print("STATUS ");
  Serial.print(coverOpen);
  Serial.print(" ");
  Serial.print(lightOn);
  Serial.print(" ");
  Serial.print(getTemperature());
  Serial.print(" ");
  Serial.print(printStatusPeriodically);
  Serial.print(" ");
  Serial.println(updateInterval);
}

// Opens or closes the cover and turns the light on or off, depending on the variable status.
void setActuators() {
  if (coverOpen) {
    servo.write(OPENED_ANGLE);
  } else {
    servo.write(CLOSED_ANGLE);
  }

  if (lightOn) {
    digitalWrite(OPTO_PIN, LOW);
  } else {
    digitalWrite(OPTO_PIN, HIGH);
  }

  delay(500); // Give it some time for the actuators to activate
}

// This command prints the version of this firmware. For example: "VERSION 1.00b"
void cmd_version(MyCommandParser::Argument *args, char *response) {
  Serial.print("VERSION ");
  Serial.println(VERSION);
}

// This command prints the status of the device
void cmd_status(MyCommandParser::Argument *args, char *response) {
  printStatus();
}

// This command opens the cover
void cmd_open(MyCommandParser::Argument *args, char *response) {
  coverOpen = true;
  setActuators();
  printStatus();
}

// This command closes the cover
void cmd_close(MyCommandParser::Argument *args, char *response) {
  coverOpen = false;
  setActuators();
  printStatus();
}

// This command turns the light on
void cmd_lightOn(MyCommandParser::Argument *args, char *response) {
  lightOn = true;
  setActuators();
  printStatus();
}

// This command turns the light off
void cmd_lightOff(MyCommandParser::Argument *args, char *response) {
  lightOn = false;
  setActuators();
  printStatus();
}

// This command starts to send STATUS messages every updateInterval seconds
void cmd_startUpdating(MyCommandParser::Argument *args, char *response) {
  lastUpdate = millis();
  printStatusPeriodically = true;
  printStatus();
}

// This command stops sending periodic STATUS messages
void cmd_stopUpdating(MyCommandParser::Argument *args, char *response) {
  printStatusPeriodically = false;
  printStatus();
}

// This command sets the update interval (in seconds [1,3600]) for periodic STATUS messages
void cmd_updateInterval(MyCommandParser::Argument *args, char *response) {
  int aux = args[0].asInt64;

  if ((aux > 0) && (aux <=3600)) {
    updateInterval = aux;
  }

  printStatus();
}

// Initialization of the microcontroller
void setup() {
  Serial.begin(9600);  // Start Serial port communication
  while (!Serial);

  servo.attach(SERVO_PIN);   // Initialize the servo library

  pinMode(OPTO_PIN, OUTPUT); // IPnitialize the optocopupler to turn the light on and off
  
  setActuators();            // Initialize the actuators

  // Register all available commands
  parser.registerCommand("VERSION", "", &cmd_version);
  parser.registerCommand("STATUS", "", &cmd_status);
  parser.registerCommand("OPEN", "", &cmd_open);
  parser.registerCommand("CLOSE", "", &cmd_close);
  parser.registerCommand("LON", "", &cmd_lightOn);
  parser.registerCommand("LOFF", "", &cmd_lightOff);
  parser.registerCommand("START", "", &cmd_startUpdating);
  parser.registerCommand("STOP", "", &cmd_stopUpdating);
  parser.registerCommand("INTERVAL", "i", &cmd_updateInterval);   // Needs an integer parameter [1, 3600]

  Serial.println("Telescope Flat Cover connected and initialized.");
}

// Main loop
void loop() {
  if (Serial.available()) {  // If there are messages in the serial port
    char line[128];
    size_t lineLength = Serial.readBytesUntil('\n', line, 127);  // Read serial port
    line[lineLength] = '\0';

    char response[MyCommandParser::MAX_RESPONSE_SIZE];
    parser.processCommand(line, response);   // Parse the message and call the appropriate callback function
  }

  if (printStatusPeriodically) {   // If we have to print STATUS messages periodically
    long currentTime = millis();

    if (currentTime - lastUpdate > updateInterval * 1000) {   // If the last STATUS message was more than updateInterval seconds ago
      lastUpdate = currentTime;

      printStatus();   // Print status message
    }
  }
}