#!/usr/bin/env python2.7 

class Encoder:

	def __init__(self,a_pin,b_pin):
		#set up gpio module
		import RPi.GPIO as GPIO  
		GPIO.setmode(GPIO.BCM)

		# Define pin numbers for A/B channels on azimuth/elevation motors
		self.A_pin=a_pin
		self.B_pin=b_pin

		# Define global count variables
		self.a_count = 0

		# Set up Pins as inputs, with internal pull 
		GPIO.setup(self.A_pin, GPIO.IN)
		GPIO.setup(self.B_pin, GPIO.IN)

		# Set up rising edge detectors for each pin
		GPIO.add_event_detect(A_pin, GPIO.RISING, callback=self.A_pin_ISR)

		
	# A channel ISR
	def A_pin_ISR():
		# Check if channel A is leading channel B (A=1,B=0)
		# If channel A leads, rotation is CCW
		# Increment/Decrement position counter based on direction
		if GPIO.input(B_pin):
			#CCW
			self.a_count += 1
		else:
			#CW
			self.a_count -= 1


	# Function to translate edge count to degrees
	def count2deg(ppr):
		# ppr = pulses per rotation (rising edges per rotation)
		return (self.a_count)*360/ppr



