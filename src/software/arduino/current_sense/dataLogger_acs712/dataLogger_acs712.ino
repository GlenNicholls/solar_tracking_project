#include <Arduino.h>
#include <ACS712.h>
#include <ADA254.h>

uint8_t CS = 10;
String filename = "log.txt"; // filenames limited to 8 chars

ACS712 sensor(ACS712_30A, A0);
ADA254 sdLogger(CS);

void setup() 
{
  // init UART
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // This method calibrates zero point of sensor,
  // It is not necessary, but may positively affect the accuracy
  // Ensure that no current flows through the sensor at this moment
  sensor.calibrate();

  sdLogger.Init();
  sdLogger.WriteFileLine(filename,"Volts[V],Current[A],Power[W]");
}

void loop() 
{
  String dataToLog = "";
  
  // Get current from sensor
  float I = sensor.getCurrentDC();
  float V = sensor.getVoltageDC();
  float P = sensor.getPowerDC();
  
  // Send it to serial
  //Serial.println(String("I = ") + I + " A");
  dataToLog = String(V) + "," + String(I) + "," + String(P);
  Serial.println(String("I = ") + I + "A," + String("V = ") + V + "V," + String("P = ") + P + "W");

  sdLogger.WriteFileLine(filename, dataToLog);
  
  // Wait one second before the new cycle
  delay(1000);
}
