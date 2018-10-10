#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define VBATPIN A7

// called this way, it uses the default address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();
// you can also call it with a different address you want
//Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x41);
// you can also call it with a different address and I2C interface
//Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(&Wire, 0x40);

// Depending on your servo make, the pulse width min and max may vary, you 
// want these to be as small/large as possible without hitting the hard stop
// for max range. You'll have to tweak them as necessary to match the servos you
// have!
#define SERVOMIN  200 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  600 // this is the 'maximum' pulse length count (out of 4096)

// our servo # counter
uint8_t servonum = 0;
uint8_t ELservo = 0;
uint8_t AZservo = 1;
float perDiffThreshold = 0.1;

void setup() {
  // put your setup code here, to run once:
  // initialize digital pin 13 as an output.
  pinMode(13, OUTPUT);

  Serial.begin(9600);
  Serial.println("Servo Test!");

  pwm.begin();
  pwm.setPWMFreq(60);  // Analog servos run at ~60 Hz updates
  delay(10);
}

// e.g. setServoPulse(0, 0.001) is a ~1 millisecond pulse width. its not precise!
void setServoPulse(uint8_t n, double pulse) {
  double pulselength;
  
  pulselength = 1000000;   // 1,000,000 us per second
  pulselength /= 60;   // 60 Hz
  Serial.print(pulselength); Serial.println(" us per period"); 
  pulselength /= 4096;  // 12 bits of resolution
  Serial.print(pulselength); Serial.println(" us per bit"); 
  pulse *= 1000000;  // convert to us
  pulse /= pulselength;
  Serial.println(pulse);
  pwm.setPWM(n, 0, pulse);
}

float getPerDiff(int v1, int v2)
{
  return (v1-v2)/((v1+v2)/2.0);
}

float getAvg(float diff1, float diff2)
{
  return (diff1+diff2)/2;
}

void measureBattery()
{
  float measuredvbat = analogRead(VBATPIN);
  measuredvbat *= 2;    // we divided by 2, so multiply back
  measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
  measuredvbat /= 1024; // convert to voltage
  Serial.print("VBat: " ); Serial.println(measuredvbat);
}

uint16_t convertDegreesToPulselength(uint16_t degrees)
{
  return map(degrees, 0, 180, SERVOMIN, SERVOMAX);
}

void servoTest()
{
  // Drive each servo one at a time
  Serial.println(servonum);
  for (uint16_t pulselen = SERVOMIN; pulselen < SERVOMAX; pulselen++) {
    pwm.setPWM(servonum, 0, pulselen);
  }

  delay(500);
  for (uint16_t pulselen = SERVOMAX; pulselen > SERVOMIN; pulselen--) {
    pwm.setPWM(servonum, 0, pulselen);
  }

  delay(500);

  servonum ++;
  if (servonum > 1) servonum = 0;
}

int evalHorizontal(float avgDiffHorizontal)
{
  if (abs(avgDiffHorizontal) > perDiffThreshold)
  {
    if (avgDiffHorizontal < 0) // LR > LL
    {
      //Serial.println("Move Left");
      return 1; //move left
    }
    else // LL > LR
    {
      //Serial.println("Move Right");
      return -1; //move right
    }
  }
  return 0; //don't move
}

//TODO: can use just one eval function fo both vertical and horizontal
int evalVertical(float avgDiffVertical)
{
  if (abs(avgDiffVertical) > perDiffThreshold)
  {
    if (avgDiffVertical < 0) // UR > UL
    {
      //Serial.println("Move Up");
      return -1; //move up
    }
    else
    {
      //Serial.println("Move Down");
      return 1; //move down
    }
  }
  return 0; //don't move
}

void readSensor(int degVertical, int degHorizontal)
{ 
  int multiplier = 5;
  int UL = analogRead(A0);
  int UR = analogRead(A1);
  int LL = analogRead(A2);
  int LR = analogRead(A3);

  float perDiffUpper = getPerDiff(UL,UR);
  float perDiffLower = getPerDiff(LL,LR);
  float perDiffLeft = getPerDiff(UL,LL);
  float perDiffRight = getPerDiff(UR,LR);
  
  float avgDiffHorizontal = getAvg(perDiffUpper, perDiffLower);
  float avgDiffVertical = getAvg(perDiffLeft,perDiffRight);

  int moveHorizontal = evalHorizontal(avgDiffHorizontal);
  int moveVertical = evalVertical(avgDiffVertical);
  if (moveHorizontal == 1)
  {
    Serial.println("Move Left");
    pwm.setPWM(AZservo, 0, convertDegreesToPulselength(degHorizontal + (moveHorizontal*multiplier)));
    Serial.println("Moved Left 5 degrees");
  }
  else if (moveHorizontal == -1)
  {
    Serial.println("Move Right");
    pwm.setPWM(AZservo, 0, convertDegreesToPulselength(degHorizontal + (moveHorizontal*multiplier)));
    Serial.println("Moved Right 5 degrees");
  }
  
  if (moveVertical == 1)
  {
    Serial.println("Move Down");
    pwm.setPWM(ELservo, 0, convertDegreesToPulselength(degVertical + (moveVertical*multiplier)));
    Serial.println("Moved Down 5 degrees");
  }
  else if (moveVertical == -1)
  {
    Serial.println("Move Up");
    pwm.setPWM(ELservo, 0, convertDegreesToPulselength(degVertical + (moveVertical*multiplier)));
    Serial.println("Moved Up 5 degrees");
  }
  
  Serial.print("ADC0-UL: ");
  Serial.println(UL);
  Serial.print("ADC1-UR: ");
  Serial.println(UR);
  Serial.print("ADC2-LL: ");
  Serial.println(LL);
  Serial.print("ADC3-LR: ");
  Serial.println(LR);
  Serial.println(avgDiffVertical);
  Serial.println(avgDiffHorizontal);
  Serial.println("---------------------");
}

void loop() {

  measureBattery();
  
  // put your main code here, to run repeatedly:
  digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);              // wait for a second
  digitalWrite(13, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);              // wait for a second

  int degVertical = 10;
  int degHorizontal = 0;

  //degVertical = 170;
  //degHorizontal = 180;
  Serial.println("Moved to 0 degrees");
  pwm.setPWM(ELservo, 0, convertDegreesToPulselength(degVertical));
  pwm.setPWM(AZservo, 0, convertDegreesToPulselength(degHorizontal));

  delay(100000);
  pwm.setPWM(ELservo, 0, convertDegreesToPulselength(degVertical));
  //pwm.setPWM(AZservo, 0, convertDegreesToPulselength(degHorizontal));
  //Serial.println("Moved to 0 degrees");
  //readSensor(degVertical, degHorizontal);
  //delay(10000);
  degHorizontal = 60;
  //pwm.setPWM(ELservo, 0, convertDegreesToPulselength(degVertical));
  pwm.setPWM(AZservo, 0, convertDegreesToPulselength(degHorizontal));
  Serial.println("Moved to 60 degrees");
  delay(5000);
  readSensor(degVertical, degHorizontal);
  delay(5000);
  degHorizontal = 120;
  //pwm.setPWM(ELservo, 0, convertDegreesToPulselength(degVertical));
  pwm.setPWM(AZservo, 0, convertDegreesToPulselength(degHorizontal));
  Serial.println("Moved to 120 degrees");
  delay(5000);
  readSensor(degVertical, degHorizontal);
  delay(5000);
  degHorizontal = 180;
  //pwm.setPWM(ELservo, 0, convertDegreesToPulselength(degVertical));
  //pwm.setPWM(AZservo, 0, convertDegreesToPulselength(degHorizontal));
  //Serial.println("Moved to 180 degrees");
  //readSensor(degVertical, degHorizontal);
  //delay(10000);
  //servoTest();
}
