#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
 
Adafruit_PWMServoDriver servoDriver = Adafruit_PWMServoDriver(0x40);

int hipZeroDeg = 90;
int femurZeroDeg = 90;
int tibiaZeroDeg = 90;
 
int minServoTicks = 30;
int maxServoTicks = 575;

int hipPosDeg = 110;
int femurPosDeg = 85;
int tibiaPosDeg = 113;

int hipServos[] = {0, 1, 2, 3};
int hipServosAdjustment[] = {20, -5, 0, 0};

int femurServos[] = {8, 9, 10, 11};
int femurServosAdjustment[] = {0, 0, 0, 0};

int tibiaServos[] = {4, 5, 6, 7};
int tibiaServosAdjustment[] = {0, 0, 0, 0};

int hipCommandDeg, 
    femurCommandDeg, 
    tibiaCommandDeg;
 
void setup() {
 
  Serial.begin(115200);
  servoDriver.begin();
  servoDriver.setPWMFreq(50);
 
}

void loop() {

  int hipDeltaDeg = hipPosDeg - hipZeroDeg;
  int femurDeltaDeg = femurPosDeg - femurZeroDeg;
  int tibiaDeltaDeg = tibiaPosDeg - tibiaZeroDeg;
  
  
  for (int i = 0; i < sizeof(hipServos) / sizeof(hipServos[0]); i++) {
    if (i == 0){
      hipCommandDeg = hipZeroDeg + hipDeltaDeg;
    }
    else if (i == 1){
      hipCommandDeg = hipZeroDeg - hipDeltaDeg;
    }
    else if (i == 2){
      hipCommandDeg = hipZeroDeg + hipDeltaDeg;
    }
    else {
      hipCommandDeg = hipZeroDeg - hipDeltaDeg;
    }
    int hipTicks = map(hipCommandDeg, 0, 180, minServoTicks, maxServoTicks);
    int servoCommand = hipTicks + hipServosAdjustment[i];
    servoDriver.setPWM(hipServos[i], 0, servoCommand);
  }

  for (int i = 0; i < sizeof(femurServos) / sizeof(femurServos[0]); i++) {
    if (i == 1 || i == 2){
      femurCommandDeg = femurZeroDeg + femurDeltaDeg;
    }
    else {
      femurCommandDeg = femurZeroDeg - femurDeltaDeg;
    }

    int femurTicks = map(femurCommandDeg, 0, 180, minServoTicks, maxServoTicks);
    int servoCommand = femurTicks + femurServosAdjustment[i];
    servoDriver.setPWM(femurServos[i], 0, servoCommand);
  }

  for (int i = 0; i < sizeof(tibiaServos) / sizeof(tibiaServos[0]); i++) {
    if (i == 1 || i == 2){
      tibiaCommandDeg = tibiaZeroDeg + tibiaDeltaDeg;
    }
    else {
      tibiaCommandDeg = tibiaZeroDeg - tibiaDeltaDeg;
    }
    
    int tibiaTicks = map(tibiaCommandDeg, 0, 180, minServoTicks, maxServoTicks);
    int servoCommand = tibiaTicks + tibiaServosAdjustment[i];
    servoDriver.setPWM(tibiaServos[i], 0, servoCommand);
  }

  delay(50);
}