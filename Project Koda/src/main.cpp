#include <Arduino.h>
#include <ESP32Servo.h>

Servo servoD, servoA;
int servoPin1 = 25;
int servoPin2 = 26;

void setup() {
  // put your setup code here, to run once:
  servoD.attach(servoPin1);
  servoA.attach(servoPin2);
  Serial.begin(115200);
}


void setKinematicAngles(int angleA, int angleD) {
  int servoAnglesA = angleA;
  int servoAnglesD = angleD - 90;
  servoD.write(servoAnglesD); // right (d)
  servoA.write(servoAnglesA); // left (a)
}

void loop() {
  setKinematicAngles(72, 106);
  delay(2000);
  setKinematicAngles(70, 139);
  delay(1000);
  setKinematicAngles(72, 106);
  delay(150);
  setKinematicAngles(70, 139);
  delay(1000);

}


