#include <ACS712.h>

ACS712 sensor(ACS712_30A, A0);


void setup() 
{
  // init UART
  Serial.begin(9600);

  // This method calibrates zero point of sensor,
  // It is not necessary, but may positively affect the accuracy
  // Ensure that no current flows through the sensor at this moment
  sensor.calibrate();
}

void loop() 
{
  // Get current from sensor
  float I = sensor.getCurrentDC();
  float V = sensor.getVoltageDC();
  float P = sensor.getPowerDC();
  
  // Send it to serial
  //Serial.println(String("I = ") + I + " A");
  Serial.println(String("I = ") + I + "A," + String("V = ") + V + "V," + String("P = ") + P + "W");

  // Wait one second before the new cycle
  delay(1000);
}
