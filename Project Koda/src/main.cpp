
#include <Arduino.h>
#include <ESP32Servo.h>
#include "GaitLib.h"
#include "GaitLookupTable.h"

Servo servoD, servoA;
int servoPin1 = 25;
int servoPin2 = 26;

// Path storage
const int maxPathPoints = 150;
Point curvePoints[maxPathPoints];
ServoAngles pathAngles[maxPathPoints];
int pathLength = 0;

void setup() {
  servoD.attach(servoPin1);
  servoA.attach(servoPin2);
  Serial.begin(115200);

  // Define half-flat-ellipse curve parameters
  CurveParams params;
  params.xc = 23;
  params.yc = -120;
  params.a = 30;
  params.b = 40;

  // Set direction: CLOCKWISE or COUNTERCLOCKWISE
  CurveDirection direction = COUNTERCLOCKWISE; // Change to CLOCKWISE for clockwise gait

  // Generate curve points
  int curveCount = generateCurvePoints(HALF_FLAT_ELLIPSE, params, curvePoints, maxPathPoints, direction);

  // Match curve points to lookup table
  pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
}

void setKinematicAngles(int angleA, int angleD) {
  int servoAnglesA = angleA;
  int servoAnglesD = angleD - 90;
  servoD.write(servoAnglesD); // right (d)
  servoA.write(servoAnglesA); // left (a)
}

void followPath() {
  Serial.println("Following path with angles:");
  for (int i = 0; i < pathLength; i++) {
    setKinematicAngles(pathAngles[i].thetaA, pathAngles[i].thetaD);
    Serial.print("Angle A: ");
    Serial.print(pathAngles[i].thetaA);
    Serial.print(", Angle D: ");
    Serial.println(pathAngles[i].thetaD);
    delay(25); // Adjust delay as needed
  }
}

void loop() {
  followPath();
  delay(1000); // Pause before repeating
}


