#include <stdlib.h>
#include <SoftwareSerial.h>
#include <ACS712.h>

uint8_t calcMinWidth = 4;
uint8_t calcPrecision = 4;
uint8_t charWidth = calcMinWidth + calcPrecision;

uint8_t rxPin = 3;
uint8_t txPin = 2;
String filename = "log.txt"; // filenames limited to 8 chars

ACS712 sensor(ACS712_30A, A0);
SoftwareSerial serInterface(rxPin, txPin); 

void setup() 
{
  // init UART for USB
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // init software serial via GPIO
  serInterface.begin(9600);
  
  // This method calibrates zero point of sensor,
  // It is not necessary, but may positively affect the accuracy
  // Ensure that no current flows through the sensor at this moment
  sensor.calibrate();


  serInterface.println("Volts[V],Current[A],Power[W]");
}

void loop() 
{
  String dataToLog = "";
  
  // Get current from sensor
  float I = sensor.getCurrentDC();
  float V = sensor.getVoltageDC();
  float P = sensor.getPowerDC();
  
  char I_char[charWidth];
  char V_char[charWidth];
  char P_char[charWidth];
  
  dtostrf(I, calcMinWidth, calcPrecision, I_char);
  dtostrf(V, calcMinWidth, calcPrecision, V_char);
  dtostrf(P, calcMinWidth, calcPrecision, P_char);

  // Send it to serial
  dataToLog = String(V_char) + "," + String(I_char) + "," + String(P_char);

  //if (serInterface.available()) {
    serInterface.println(dataToLog); // send data to uart gpio
  //}
  //else {
    Serial.println(dataToLog);
  //}
  // Wait one second before the new cycle
  delay(500);
}
