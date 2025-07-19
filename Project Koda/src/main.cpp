// Include Wire Library for I2C
#include <Arduino.h>
#include <Wire.h>
 
// Include Adafruit PCA9685 Servo Library
#include <Adafruit_PWMServoDriver.h>
 
// Creat object to represent PCA9685 at default I2C address
Adafruit_PWMServoDriver pca9685 = Adafruit_PWMServoDriver(0x40);
 
// Define maximum and minimum number of "ticks" for the servo motors
// Range from 0 to 4095
// This determines the pulse width
 
int servomin = 30;  // Minimum value (can be changed at runtime)
int servomax = 575; // Maximum value (can be changed at runtime)
int frontOffset = 0;
 
// Define servo motor connections (expand as required)
#define SER0  0   //Servo Motor 0 on connector 0
 
// Variables for Servo Motor positions (expand as required)
int pwm0;

int servos[] = {0, 1, 2, 3};
 
void setup() {
 
  // Serial monitor setup
  Serial.begin(115200);
 
  // Print to monitor
  Serial.println("PCA9685 Servo Test");
 
  // Initialize PCA9685
  pca9685.begin();
 
  // Set PWM Frequency to 50Hz
  pca9685.setPWMFreq(50);
 
}

void loop() {
  static int posDegrees = 90;
  static String inputString = "";
  static bool stringComplete = false;

  // Read serial input
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n' || inChar == '\r') {
      if (inputString.length() > 0) stringComplete = true;
    } else {
      inputString += inChar;
    }
  }

  if (stringComplete) {
    inputString.trim();
    if (inputString.startsWith("min ")) {
      int val = inputString.substring(4).toInt();
      if (val > 0 && val < servomax) {
        servomin = val;
        Serial.print("Set servomin to: ");
        Serial.println(servomin);
      }
    } else if (inputString.startsWith("max ")) {
      int val = inputString.substring(4).toInt();
      if (val > servomin && val < 4096) {
        servomax = val;
        Serial.print("Set servomax to: ");
        Serial.println(servomax);
      }
    } else if (inputString.startsWith("deg ")) {
      int val = inputString.substring(4).toInt();
      if (val >= 0 && val <= 180) {
        posDegrees = val;
        Serial.print("Set angle to: ");
        Serial.println(posDegrees);
      }
    } else if (inputString.startsWith("off ")) {
      int val = inputString.substring(4).toInt();
      if (val >= 0 && val <= 180) {
        frontOffset = val;
        Serial.print("Set front offset to: ");
        Serial.println(frontOffset);
      }
    } else if (inputString == "show") {
      Serial.print("servomin: "); Serial.println(servomin);
      Serial.print("servomax: "); Serial.println(servomax);
      Serial.print("angle: "); Serial.println(posDegrees);
      Serial.print("front offset: "); Serial.println(frontOffset);
    } else {
      Serial.println("Commands: min <val>, max <val>, deg <val>, show");
    }
    inputString = "";
    stringComplete = false;
  }

  pwm0 = map(posDegrees, 0, 180, servomin, servomax);
  // Only update servo 0 for calibration

  pca9685.setPWM(0, 0, pwm0 + 20);
  pca9685.setPWM(1, 0, pwm0 - 5);
  pca9685.setPWM(2, 0, pwm0);
  pca9685.setPWM(3, 0, pwm0);

  delay(50); // Slow down loop for stability
}