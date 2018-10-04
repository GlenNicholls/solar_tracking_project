#!/usr/bin/env python2.7 

import RPi.GPIO as GPIO  
GPIO.setmode(GPIO.BCM)

# Define pin numbers for A/B channels on azimuth/elevation motors
A_az=23
B_az=24

A_el=12
B_el=16

# Define global count variables
a_az_count = 0
b_az_count = 0
a_el_count = 0
b_el_count = 0

# Set up Pins as inputs, with internal pull 
GPIO.setup(A_az, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(B_az, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

GPIO.setup(A_el, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(B_el, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# A channel azimuth ISR
def A_az_ISR(A_az):
	global a_az_count
	# Check if channel A is leading channel B (A=1,B=0)
	# If channel A leads, rotation is CCW
	# Increment/Decrement position counter based on direction
	if(GPIO.input(A_az) != GPIO.input(B_az)):
		#CCW
		a_az_count -= 1
	else:
		#CW
		a_az_count += 1
		
# B channel azimuth ISR
def B_az_ISR(B_az):
	global b_az_count
	# Check if channel A is leading channel B (A=1,B=0)
	# If channel A leads, rotation is CCW
	# Increment/Decrement position counter based on direction
	if(GPIO.input(A_az) > GPIO.input(B_az)):
		#CCW
		b_az_count -= 1
	else:
		#CW
		b_az_count += 1
	
# A channel elevation ISR
def A_el_ISR(A_el):
	global a_el_count
	# Check if channel A is leading channel B (A=1,B=0)
	# If channel A leads, rotation is CCW
	# Increment/Decrement position counter based on direction
	if(GPIO.input(A_el) > GPIO.input(B_el)):
		#CCW
		a_el_count -= 1
	else:
		#CW
		a_el_count += 1
		
# A channel elevation ISR
def B_el_ISR(B_el):
	global b_el_count
	# Check if channel A is leading channel B (A=1,B=0)
	# If channel A leads, rotation is CCW
	# Increment/Decrement position counter based on direction
	if(GPIO.input(A_el) > GPIO.input(B_el)):
		#CCW
		b_el_count -= 1
	else:
		#CW
		b_el_count += 1


# Set up rising edge detectors for each pin
GPIO.add_event_detect(A_az, GPIO.RISING, callback=A_az_ISR)
GPIO.add_event_detect(B_az, GPIO.RISING, callback=B_az_ISR)

GPIO.add_event_detect(A_el, GPIO.RISING, callback=A_el_ISR)
GPIO.add_event_detect(B_el, GPIO.RISING, callback=B_el_ISR)

		
# Function to translate edge count to degrees
def count2deg(a_count,b_count,ppr):
	# ppr = pulses per rotation (rising edges per rotation)
	return (a_count)*360/ppr



