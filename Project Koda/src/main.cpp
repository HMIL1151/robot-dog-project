
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
bool isAtStart = false;

void setup() {
  servoD.attach(servoPin1);
  servoA.attach(servoPin2);
  Serial.begin(115200);

  // Nothing here, all curve setup is now in loop()
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
    if (isAtStart) 
    {
      delay(1000); // Wait at start position
      isAtStart = false; // Only wait once at the start
    }
    Serial.print("Angle A: ");
    Serial.print(pathAngles[i].thetaA);
    Serial.print(", Angle D: ");
    Serial.println(pathAngles[i].thetaD);
    delay(25); // Adjust delay as needed
  }
  isAtStart = true; // Reset to wait at start for next path
}

void loop() {
  // 1. Vertical line
  // Serial.println("Executing: Vertical Line");
  // {
  //   CurveParams params;
  //   params.x0 = 50; // x position
  //   params.y0 = -120; // y start
  //   params.yc = -60;  // y end
  //   int curveCount = generateCurvePoints(VERTICAL, params, curvePoints, maxPathPoints, +1);
  //   pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
  //   followPath();
  //   delay(200);

  //   curveCount = generateCurvePoints(VERTICAL, params, curvePoints, maxPathPoints, -1);
  //   pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
  //   followPath();
  //   delay(1000);
  // }

  // // 2. Horizontal line
  // Serial.println("Executing: Horizontal Line");
  // {
  //   CurveParams params;
  //   params.x0 = 20; // x start
  //   params.xc = 80; // x end
  //   params.y0 = -100; // y position
  //   int curveCount = generateCurvePoints(HORIZONTAL, params, curvePoints, maxPathPoints, +1);
  //   pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
  //   followPath();
  //   delay(200);

  //   curveCount = generateCurvePoints(HORIZONTAL, params, curvePoints, maxPathPoints, -1);
  //   pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
  //   followPath();
  //   delay(1000);
  // }

  // // 3. Straight line (y = m*x + c)
  // Serial.println("Executing: Straight Line");
  // {
  //   CurveParams params;
  //   params.x0 = 20; // x start
  //   params.xc = 80; // x end
  //   params.m = 0.5; // slope
  //   params.c = -120; // intercept
  //   int curveCount = generateCurvePoints(LINE, params, curvePoints, maxPathPoints, +1);
  //   pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
  //   followPath();
  //   delay(200);

  //   curveCount = generateCurvePoints(LINE, params, curvePoints, maxPathPoints, -1);
  //   pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
  //   followPath();
  //   delay(1000);
  // }

  // // 4. Ellipse
  // Serial.println("Executing: Ellipse");
  // {
  //   CurveParams params;
  //   params.xc = 50; // center x
  //   params.yc = -100; // center y
  //   params.a = 30; // radius x
  //   params.b = 20; // radius y
  //   int curveCount = generateCurvePoints(ELLIPSE, params, curvePoints, maxPathPoints, +1);
  //   pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
  //   followPath();
  //   delay(200);

  //   curveCount = generateCurvePoints(ELLIPSE, params, curvePoints, maxPathPoints, -1);
  //   pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
  //   followPath();
  //   delay(1000);
  // }

  // 5. Half-flat-ellipse
  Serial.println("Executing: Half-Flat Ellipse");
  {
    CurveParams params;
    params.xc = 23;
    params.yc = -120;
    params.a = 30;
    params.b = 40;
    int curveCount = generateCurvePoints(HALF_FLAT_ELLIPSE, params, curvePoints, maxPathPoints, +1);
    pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
    followPath();
    delay(200);

    curveCount = generateCurvePoints(HALF_FLAT_ELLIPSE, params, curvePoints, maxPathPoints, -1);
    pathLength = matchCurveToLookup(curvePoints, curveCount, lookupTable, lookupCount, pathAngles, maxPathPoints);
    followPath();
    delay(1000);
  }
}


