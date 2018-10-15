/*
 * power_circuit_ctrl.c
 *
 * Created: 10/13/2018 8:01:58 PM
 * Author : Glen Nicholls
 *
 * Description:
 * -------------
 * Simple blinky implementation with interrupts
 */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
//#include <util/delay.h>


//#define F_CPU 8000000
//#define F_CPU 1000000UL


// todo: do we need this at all??
// void WDT_off(void)
// {
//     _WDR();
//
//     // CLR WDRF in MCUSR
//     MCUSR |= 0x00;
//
//     // Write 1 to WDCE and WDE
//     WDTCSR |= (1 << WDCE);
//     WDTCSR |= (1 << WDE);
//
//     // Turn off WDT
//     WDTCSR = 0x00;
// }


static inline void initInterrupts(void)
{
  // Configure INT0 interrupt mode
  MCUCR |= (0b01 << ISC00); // Mode: logic change

  // General Interrupt Mask Register
  //
  // PCIE1 : 1 Enable pin change INT
  // PCIE0 : 1 Enable pin change INT
  // INT0  : 1 Enable external interrupt
  GIMSK |= (1 << INT0) | (1 << PCIE0) | (1 << PCIE1);

  // Pin Change Mask Registers
  PCMSK0 |= (1 << PCINT7);
  PCMSK1 |= (1 << PCINT9);
}

static inline void initMCU(void)
{
  // DDRA Port Directions
  //
  // DDA7: 0 input pi_tx_hold_on PCINT7
  // DDA6: 1 DNC low-power
  // DDA5: 1 DNC low-power
  // DDA4: 1 DNC low-power
  // DDA3: 1 output pi_rx_dev_mode
  // DDA2: 1 DNC low-power
  // DDA1: 1 FAULT output
  // DDA0: 1 output en_power
  DDRA &= ~(1 << PA7);
  DDRA |= (1 << PA6) | (1 << PA5) | (1 << PA4) | (1 << PA3) |
    (1 << PA2) | (1 << PA1) | (1 << PA0);

  // Enable pullups on PA[7] input
  // Enable pullups on PA[6:0] for low-power
  PORTA |= (1 << PA7) | (1 << PA6) | (1 << PA5) | (1 << PA4) |
           (1 << PA3) | (1 << PA2) | (1 << PA1) | (1 << PA0);

  // DDRB Port Directions
  //
  // DDB3: 1 DNC low-power
  // DDB2: 0 input rtc_ALRM_N
  // DDB1: 0 input psh_button
  // DDB0: 1 DNC low-power
  DDRB &= ~( (1 << PB2) | (1 << PB1) );
  //DDRB |= (1 << PB3) | (1 << PB0);

  // Enable pullups on PB[2:1] input
  // Enable pullups on PB[3,0] for low-power
  //PORTB |= (1 << PB3) | (1 << PB2) | (1 << PB1) | (1 << PB0);
  PORTB |= (1 << PB3) | (1 << PB1) | (1 << PB0);
  PORTB &= ~(1 << PB2); // debugging pullup

  // Enable the MCUCR pullups
  MCUCR &= ~(1 << PUD);

  // todo: not sure how to configure clocks yet
//
//  // Analog Comparator Control/Status Register
//  ACSR |= (1 << ACD); // disable
//
//  // Power Reduction Register
//  //
//  // PRTIM1 : ??
//  // PRTIM0 : ??
//  // PRUSI  : ??
//  PRR |= (1 << PRADC); // disable ADC
//
//  // Sleep Mode
//  //
//  // BODS  : disable BOD during low-power?
//  // PUD   : ??
//  // BODSE : ??
//  // todo: would power-down be better since it halts clocks and only wakes on async events??
//  // todo: should SE only be enabled when desired and cleared upon wakeup??
//  MCUCR |= (1 << SE);     // Enable sleep
//  MCUCR |= (0b11 << SM0); // Mode: standby

  // Configure INT
  initInterrupts();

  // Enable global interrupts by set I-bit in SREG to 1
  sei();
}

// todo: Complete GIFR clear here
// todo: wait on this until blink is accomplished first
// todo: will an interrupt while another interrupt is being serviced cause contention on en_power??
ISR(EXT_INT0_vect)
{
  //if (PINB & (1 << PB2)) // pb2 high
  //{
  //  PORTA |= (1 << PA0); // turn LED on
  //}
  //else
  //{
  //  PORTA &= ~(1 << PA0); // turn LED off
  //}
}

ISR(PCINT0_vect)
{


  // Clear interrupt flag
  GIFR |= (1 << PCIF1);
}

ISR(PCINT1_vect)
{
  if (PINB & (1 << PB1)) // pb2 high
  {
    PORTA |= (1 << PA0); // turn LED on
  }
  else
  {
    PORTA &= ~(1 << PA0); // turn LED off
  }

  // Clear interrupt flag
  GIFR |= (1 << INTF0);
}


int main(void)
{
  initMCU();

  while (1)
  {
    //sleep_cpu();
  }

  return 0;
}

