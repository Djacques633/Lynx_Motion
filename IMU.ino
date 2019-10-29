/*
   Library: https://github.com/bolderflight/MPU9250
  Basic_I2C.ino
  Brian R Taylor
  brian.taylor@bolderflight.com

  Copyright (c) 2017 Bolder Flight Systems

  Permission is hereby granted, free of charge, to any person obtaining a copy of this software
  and associated documentation files (the "Software"), to deal in the Software without restriction,
  including without limitation the rights to use, copy, modify, merge, publish, distribute,
  sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all copies or
  substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
  BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/
/*
   Updated by Ahmad Shamshiri on July 09, 2018 for Robojax.com
   in Ajax, Ontario, Canada
   watch instrucion video for this code:
  For this sketch you need to connect:
  VCC to 5V and GND to GND of Arduino
  SDA to A4 and SCL to A5

  S20A is 3.3V voltage regulator MIC5205-3.3BM5
*/

float DECAY = .4;

#include "MPU9250.h"
double yaw = 0;
// an MPU9250 object with the MPU-9250 sensor on I2C bus 0 with address 0x68
MPU9250 IMU(Wire, 0x68);
int status;
float cxacc,cyacc,czacc = 0.0;
void setup() {
  // serial to display data
  Serial.begin(115200);
  while (!Serial) {}

  // start communication with IMU
  status = IMU.begin();
  if (status < 0) {
    Serial.println("IMU initialization unsuccessful");
    Serial.println("Check IMU wiring or try cycling power");
    Serial.print("Status: ");
    Serial.println(status);
    while (1) {}
  }
  IMU.calibrateGyro();
}

void loop() {
  // read the sensor
  delay(15);
  int res = IMU.readSensor();
  if (res < 0){
    Serial.println("ERROR");
    return;
  }
  // display the data
  double xacc = IMU.getAccelX_mss();
  double yacc = IMU.getAccelY_mss();
  double zacc = IMU.getAccelZ_mss();
  float magx = IMU.getMagX_uT();
  float magy = IMU.getMagY_uT();
  float magz = IMU.getMagZ_uT();
  float xgyro = IMU.getGyroX_rads();
  float ygyro = IMU.getGyroY_rads();
  float zgyro = IMU.getGyroZ_rads();
  
  xacc = (1-DECAY) * cxacc + DECAY * xacc;
  yacc = (1-DECAY) * cyacc + DECAY * yacc;
  zacc = (1-DECAY) * czacc + DECAY * zacc;
  cxacc = xacc;
  cyacc = yacc;
  czacc = zacc;

  xacc = ((xacc) * 3.9);
  yacc = ((yacc) * 3.9);
  zacc = ((zacc) * 3.9);
  
  float pitch = 180 * atan (xacc / sqrt(pow(yacc, 2) + pow(zacc, 2))) / M_PI;
  float roll = 180 * atan (yacc / sqrt(pow(xacc, 2) + pow(zacc, 2))) / M_PI;
  yaw = yaw + zgyro;
  String message = (String)-pitch + "," + (String)-roll + "," + (String)-yaw;
  Serial.println(message);
}
