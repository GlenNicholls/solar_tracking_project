import RPi.GPIO as GPIO  


class encoder:

  def __init__(self,a_pin,b_pin, ppr):
    # Define pin numbers for A/B channels on azimuth/elevation motors
    self.A_pin=a_pin
    self.B_pin=b_pin

    # Define pulses per revolution (2000 for chosen encoders)
    self.ppr = ppr
    
    # Define global count variables
    self.a_count = 0
    
    # Configure interrupts
    self.CFG_Encoder_Int()

  def CFG_Encoder_Int(self):
    #set up gpio module
    GPIO.setmode(GPIO.BCM)
  
    # Set up Pins as inputs, with internal pull 
    GPIO.setup(self.A_pin, GPIO.IN)
    GPIO.setup(self.B_pin, GPIO.IN)

    # Set up rising edge detectors for each pin
    GPIO.add_event_detect(A_pin, GPIO.RISING, callback=self.A_pin_ISR)
		
  # A channel ISR
  def A_pin_ISR(self):
    # Check if channel A is leading channel B (A=1,B=0)
    # If channel A leads, rotation is CCW
    # Increment/Decrement position counter based on direction
    if GPIO.input(B_pin):
      #CCW
      self.a_count += 1
    else:
      #CW
      self.a_count -= 1


  def get_degrees(self):
    return (self.a_count)*360/self.ppr
  
  def get_count(self):
    return self.a_count
