#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Bluepad32.h>

#define RXD2 16   // ESP32 receives on GPIO16
#define TXD2 17   // ESP32 transmits on GPIO17

// ===== MPU6050 Variables =====
Adafruit_MPU6050 mpu;
float alpha = 0.98;
unsigned long lastTime = 0;
float dt;
float roll = 0.0, pitch = 0.0;
float rollOffset = 0.0, pitchOffset = 0.0;
unsigned long lastSend = 0;
const unsigned long sendInterval = 20; // ms (50Hz)

// ===== Bluepad32 Variables =====
ControllerPtr myControllers[BP32_MAX_GAMEPADS];
int buttons[22];

void sendControllerIMUPacket() {
    const uint8_t START_BYTE = 0xAA;
    uint8_t packet[17];

    // 1. Start byte
    packet[0] = START_BYTE;

    // 2. IMU angles, scaled to int16_t
    int16_t roll_int  = (int16_t)(roll * 100);
    int16_t pitch_int = (int16_t)(pitch * 100);
    packet[1] = roll_int & 0xFF;
    packet[2] = (roll_int >> 8) & 0xFF;
    packet[3] = pitch_int & 0xFF;
    packet[4] = (pitch_int >> 8) & 0xFF;

    // 3. Joystick axes (int16_t, 4 axes)
    for (int i = 0; i < 4; i++) {
        int16_t axis = (int16_t)buttons[i];
        packet[5 + i*2] = axis & 0xFF;
        packet[6 + i*2] = (axis >> 8) & 0xFF;
    }

    // 4. Pack 22 buttons into 3 bytes (least significant 22 bits)
    uint32_t button_bits = 0;
    for (int i = 0; i < 22; i++) {
        if (buttons[i]) button_bits |= (1UL << i);
    }
    packet[13] = button_bits & 0xFF;
    packet[14] = (button_bits >> 8) & 0xFF;
    packet[15] = (button_bits >> 16) & 0xFF;

    // 5. Checksum: XOR of bytes 1 to 15 (not including start byte)
    uint8_t checksum = 0;
    for (int i = 1; i <= 15; i++) {
        checksum ^= packet[i];
    }
    packet[16] = checksum;

    // 6. Send packet
    Serial2.write(packet, sizeof(packet));
}


// ===== Bluepad32 Callbacks =====
void onConnectedController(ControllerPtr ctl) {
    for (int i = 0; i < BP32_MAX_GAMEPADS; i++) {
        if (myControllers[i] == nullptr) {
            myControllers[i] = ctl;
            ////Serial.printf("Controller connected, index=%d\n", i);
            break;
        }
    }
}
void onDisconnectedController(ControllerPtr ctl) {
    for (int i = 0; i < BP32_MAX_GAMEPADS; i++) {
        if (myControllers[i] == ctl) {
            myControllers[i] = nullptr;
            //Serial.printf("Controller disconnected from index=%d\n", i);
            BP32.setup(&onConnectedController, &onDisconnectedController);
            BP32.forgetBluetoothKeys();
            //Serial.println("Reconnecting...");
            break;
        }
    }
}

void processGamepad(ControllerPtr ctl) {
    // Read analog stick axes (range: -512 to 512)
    buttons[0] = ctl->axisX();
    buttons[1] = ctl->axisY();
    buttons[2] = ctl->axisRX();
    buttons[3] = ctl->axisRY();

    // Parse D-pad values
    uint8_t dpad = ctl->dpad();
    buttons[4] = (dpad & 0x08) ? 1 : 0; // Left
    buttons[5] = (dpad & 0x04) ? 1 : 0; // Right
    buttons[6] = (dpad & 0x01) ? 1 : 0; // Up
    buttons[7] = (dpad & 0x02) ? 1 : 0; // Down

    // Parse face buttons and shoulder buttons
    uint16_t btn = ctl->buttons();
    buttons[8]  = (btn & 0x0004) ? 1 : 0;  // Square
    buttons[9]  = (btn & 0x0002) ? 1 : 0;  // Circle
    buttons[10] = (btn & 0x0008) ? 1 : 0;  // Triangle
    buttons[11] = (btn & 0x0001) ? 1 : 0;  // Cross
    buttons[12] = (btn & 0x0010) ? 1 : 0;  // L1
    buttons[13] = (btn & 0x0040) ? 1 : 0;  // L2 (digital press)
    buttons[14] = (btn & 0x0020) ? 1 : 0;  // R1
    buttons[15] = (btn & 0x0080) ? 1 : 0;  // R2 (digital press)
    buttons[16] = (btn & 0x0100) ? 1 : 0;  // L3
    buttons[17] = (btn & 0x0200) ? 1 : 0;  // R3
    buttons[18] = (btn & 0x8000) ? 1 : 0;  // Touchpad click

    // Parse misc buttons
    uint8_t misc = ctl->miscButtons();
    buttons[19] = (misc & 0x02) ? 1 : 0; // Share
    buttons[20] = (misc & 0x04) ? 1 : 0; // Options
    buttons[21] = (misc & 0x01) ? 1 : 0; // PS

    // Print stick values continuously
    //Serial.printf("LX:%4d  LY:%4d  RX:%4d  RY:%4d  ", 
                  // buttons[0], buttons[1], buttons[2], buttons[3]);

    // Print pressed buttons
    // bool anyPressed = false;
    // if (buttons[4]) { //Serial.print("DPad Left "); anyPressed = true; }
    // if (buttons[5]) { //Serial.print("DPad Right "); anyPressed = true; }
    // if (buttons[6]) { //Serial.print("DPad Up "); anyPressed = true; }
    // if (buttons[7]) { //Serial.print("DPad Down "); anyPressed = true; }

    // if (buttons[8])  { //Serial.print("Square "); anyPressed = true; }
    // if (buttons[9])  { //Serial.print("Circle "); anyPressed = true; }
    // if (buttons[10]) { //Serial.print("Triangle "); anyPressed = true; }
    // if (buttons[11]) { //Serial.print("Cross "); anyPressed = true; }

    // if (buttons[12]) { //Serial.print("L1 "); anyPressed = true; }
    // if (buttons[13]) { //Serial.print("L2 "); anyPressed = true; }
    // if (buttons[14]) { //Serial.print("R1 "); anyPressed = true; }
    // if (buttons[15]) { //Serial.print("R2 "); anyPressed = true; }
    // if (buttons[16]) { //Serial.print("L3 "); anyPressed = true; }
    // if (buttons[17]) { //Serial.print("R3 "); anyPressed = true; }
    // if (buttons[18]) { //Serial.print("Touchpad "); anyPressed = true; }

    // if (buttons[19]) { //Serial.print("Share "); anyPressed = true; }
    // if (buttons[20]) { //Serial.print("Options "); anyPressed = true; }
    // if (buttons[21]) { //Serial.print("PS "); anyPressed = true; }

    //Serial.println(); // Always print newline so stick values are on separate lines
    delay(20); // 50Hz refresh
}

void processControllers() {
    for (auto myController : myControllers) {
        if (myController && myController->isConnected() && myController->hasData() && myController->isGamepad()) {
            processGamepad(myController);
        }
    }
}

// ===== SETUP =====
void setup() {
    Serial.begin(460800);
    while (!Serial) delay(10);

    // --- MPU6050 INIT ---
    if (!mpu.begin()) {
        //Serial.println("Failed to find MPU6050 chip");
        while (1) delay(10);
    }
    //Serial.println("MPU6050 Found!");
    mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    delay(100);

    // --- Calibrate MPU6050 ---
    //Serial.println("Calibrating... keep device still");
    const int samples = 100;
    float sumRoll = 0, sumPitch = 0;
    for (int i = 0; i < samples; i++) {
        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);
        float accelRoll  = atan2(a.acceleration.y, a.acceleration.z) * 180 / PI;
        float accelPitch = atan(-a.acceleration.x / 
                            sqrt(a.acceleration.y * a.acceleration.y + 
                                a.acceleration.z * a.acceleration.z)) * 180 / PI;
        sumRoll += accelRoll;
        sumPitch += accelPitch;
        delay(5);
    }
    rollOffset = sumRoll / samples;
    pitchOffset = sumPitch / samples;
    //Serial.print("Offsets -> Roll: ");
    //Serial.print(rollOffset, 2);
    //Serial.print(" Pitch: ");
    //Serial.println(pitchOffset, 2);

    lastTime = millis();

    // --- Bluepad32 INIT ---
    BP32.setup(&onConnectedController, &onDisconnectedController);
    BP32.forgetBluetoothKeys();

    Serial2.begin(406800, SERIAL_8N1, RXD2, TXD2);
}

// ===== LOOP =====
void loop() {
    // --- MPU6050 READ ---
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    unsigned long now = millis();
    dt = (now - lastTime) / 1000.0;
    lastTime = now;

    float accelRoll  = atan2(a.acceleration.y, a.acceleration.z) * 180 / PI - rollOffset;
    float accelPitch = atan(-a.acceleration.x / 
                        sqrt(a.acceleration.y * a.acceleration.y + 
                            a.acceleration.z * a.acceleration.z)) * 180 / PI - pitchOffset;

    float gyroRollRate  = g.gyro.x * 180 / PI;
    float gyroPitchRate = g.gyro.y * 180 / PI;

    roll  = alpha * (roll + gyroRollRate * dt)  + (1 - alpha) * accelRoll;
    pitch = alpha * (pitch + gyroPitchRate * dt) + (1 - alpha) * accelPitch;

    //Serial.print("IMU Roll: ");
    //Serial.print(roll, 2);
    //Serial.print(" | Pitch: ");
    //Serial.print(pitch, 2);
    //Serial.print(" || ");

    // --- Bluepad32 READ ---
    if (BP32.update()) {
        processControllers();
    } else {
        //Serial.println(); // To end the IMU line if no controller is connected
    }

    unsigned long nowSend = millis();
    if (nowSend - lastSend >= sendInterval) {
        sendControllerIMUPacket();
        lastSend = now;
    }

    delay(10); // Adjust as needed, main loop runs ~100Hz
}