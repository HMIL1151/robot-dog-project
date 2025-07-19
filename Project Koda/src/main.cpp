
#include <Arduino.h>
#include <ESP32Servo.h>
#include "GaitLib.h"
#include "GaitLookupTable.h"

Servo servoD, servoA;
int servoPinD = 25;
int servoPinA = 27;



void setup() {
  servoD.attach(servoPinD);
  servoA.attach(servoPinA);
  Serial.begin(115200);

}



void loop() {
  servoA.write(111);   //79
  servoD.write(50);  //130
}


