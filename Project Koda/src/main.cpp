
#include <Arduino.h>
#include <ESP32Servo.h>
#include "GaitLib.h"
#include "GaitLookupTable.h"

Servo servoD, servoA;
int servoPin1 = 25;
int servoPin2 = 26;



void setup() {
  servoD.attach(servoPin1);
  servoA.attach(servoPin2);
  Serial.begin(115200);

}



void loop() {
  servoA.write(79);   //79
  servoD.write(130);  //130
}


