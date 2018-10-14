/*
 * example_blinky.c
 *
 * Created: 10/11/2018 4:09:02 PM
 * Author : Glen Nicholls
 */ 

#include <avr/io.h>
#include <util/delay.h>

#define F_CPU 8000000
//#define F_CPU 1000000UL


int main(void)
{
	// set pin10/PA3 as output
	DDRA = (1 << PA3);
	
	// loop
    while (1) 
    {
		// set PB1 high
		PORTA = (1 << PA3);
		
		_delay_ms(200);
		
		// set PB1 low
		PORTA &= ~(1 << PA3); // or PORTA = 0 for all low
		
		_delay_ms(200);
    }
}

