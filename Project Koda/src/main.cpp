#include <Arduino.h>
#include <ESP32Servo.h>


Servo myServo1, myServo2;
int servoPin1 = 25;
int servoPin2 = 26;

void setup() {
  // put your setup code here, to run once:
  myServo1.attach(servoPin1);
  myServo2.attach(servoPin2);
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  myServo1.write(90 - 25);
  myServo2.write(90 - 45);
}
