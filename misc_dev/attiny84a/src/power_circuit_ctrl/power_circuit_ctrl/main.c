/*
 * power_circuit_ctrl.c
 *
 * Created: 10/13/2018 8:01:58 PM
 * Author : Glen Nicholls
 *
 * Description:
 * -------------
 *    This device will control the load switch output that provides power to an
 *    external device such as a Raspberry Pi or other uC that consumes too much
 *    power.
 *
 *    Goal #1: DON'T KILL THE BROCCOLI!!!
 *
 * Input Pins:
 * -----------
 *    Reference schematic for specific net names
 *
 *    DS3231 INT_N (RTC):
 *        The RTC is used to maintain time while the raspberry pi or other device
 *        is turned off and does not have power. Before shutdowns, the device on
 *        the switched power circuit will set alarms before shutting down so that
 *        the uC can manage turning power back on during these alarm events.
 *
 *        1. During an alarm event, when the RTC time matches alarm registers,
 *           the output of the RTC will be driven LOW
 *        2. Low-going edge will cause interrupt. At this time, this sw will
 *           enable the TPS22958 load switch to provide the pi with power.
 *        3. Pi will assert pi_tx_hold_on to let uC know it has reset the RTC
 *           alarm. The pi will also verify the RTC alarm registers are cleared.
 *        4. When the alarm register is cleared, this pin will be pulled high
 *        5. uC will hold en_power high, enter low-power sleep, and wait for the
 *           next interrupt event
 *
 *    pi_tx_hold_on:
 *        This is an acknowledgement by the pi that it has turned on and is
 *        currently busy with its application. When this pin goes low, it
 *        is a notification to the uC that it needs to wait for the pi to
 *        safely shutdown before pulling the plug.
 *
 *        1. This pin should be an interrupt looking for a low-going edge
 *        2. After power is applied to Pi, this pin will be driven high
 *        3. When this pin is driven low, i.e. the Pi has shutdown, this routine
 *           will continue to hold the en_power high for a certain amount of time.
 *        4. After desired time has been reached, the uC will drive en_power low
 *           to disable the power to the Pi.
 *        5. uC will enter low-power sleep and wait for the next interrupt event.
 *
 *    Push Button Event:
 *        This is a manual override by the user that development will commence on
 *        the device.
 *
 *        todo: solidify whether pi will be off periodically throughout the day as
 *        this may influence the algorithm and checks during this stage!
 *
 *        todo: this should be implemented as dev_mode and power on as those states
 *              from pi perspective should be the same. Don't want to interrupt
 *              software operation, should just tell pi that algorithm can't initiate
 *              shutdown if it periodically shuts down. If so, need to ensure that the
 *              pi recognizes shutdown command to set next alarm as previous one may
 *              have passed, or will pass while pi is in the middle of shutting down.
 *
 *        1. This pin is normally pulled high
 *        2. Push button is debounced in analog, but will smooth just in case
 *        3. When there is a low-going edge, an interrupt will be issued.
 *        4. The uC will service this interrupt by driving the pi_rx_dev_mode
 *           pin high, driving en_power high, and waiting for the Pi to assert
 *           pi_tx_hold_on.
 *        5. uC will then follow pi_tx_hold_on description above
 *
 * Output Pins:
 * ------------
 *    en_power:
 *        This pin is a digital logic control for the TPS22958 load switch that
 *        controlls power to the pi. When this pin is driven high, the load switch
 *        output will follow-suit.
 *
 *    FAULT:
 *        FAULT conditions are a safe-guard in place of events that could either
 *        be induced by the uC, or the Pi's failure to perform routine events
 *        that the uC requires to maintain integrity of the power circuit. While
 *        the pi cannot be directly damaged by cutting power, the SD card most
 *        certainly can! Thus, FAULT conditions will be fed into the pi so the
 *        user does not need to routinely check the FAULT LED. In any case, when
 *        the pi or other device does not adhere to the standards the uC needs to
 *        properly operate, it is entirely possible that cutting power would
 *        interrupt application code which could be detrimental.
 *
 *        todo: software on pi should have this as interrupt to log the event
 *        todo: should this ever be cleared by uC or user intervention and reboot?
 *
 *        1. This output pin will be driven high during any fault conditions to
 *           light an LED for the user if anything doesn't work.
 *        2. If the pi does not assert the pi_tx_hold_on after a certain amount of time
 *           the uC will drive this pin high.
 *        3. To check if the pi GPIO/SW is broken, the uC will check the DS3231 pin to see
 *           if the alarm flag has been cleared.
 *        4. If the alarm flag has been cleared and the pi_tx_hold_on is never driven high,
 *           the FAULT pin will be held high.
 *        5. the uC will continue monitoring the pin for a long time. If after this time the
 *           pin is never driven high, the uC will then assume the pi has safely shutdown
 *           and drive the en_power low.
 *        6. todo: During this FAULT condition, the uC will NOT enter a low-power sleep to wait
 *           for an interrupt, it will continue to hold this pin high and will pseudo-
 *           take over for the RTC??
 *        7. SW in the Pi or other nevice needs a way to notify the user to analyze
 *           what went wrong and test all startup functionality.
 *
 *    pi_rx_dev_mode:
 *        During a push button event, this will force pi to boot into a development
 *        mode where it will not run main application, but instead be powered on
 *        to develop.
 *
 *        todo: solidify whether pi will be off during the day as this may influence
 *        the algorithm and checks during this stage!
 *
 *        1. When a push button event occurs, the en_power pin will be driven high
 *           if it wasn't already.
 *        2. This pin will then be driven high to notify the pi that it needs to
 *           enter a development mode; i.e. the pi should not shutdown unless the
 *           user specifies it do so. Reference todo:
 */

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
//#include <util/delay.h>


#define F_CPU 8000000
//#define F_CPU 1000000UL

// used for a very short delay
#define _NOP() do { __asm__ __volatile__ ("nop"); } while (0)


// todo: implement this when the time comes
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
  // DDA6: 0 input MOSI low-power
  // DDA5: 0 input MISO low-power
  // DDA4: 0 input SCK  low-power
  // DDA3: 1 output pi_rx_dev_mode
  // DDA2: 0 DNC low-power
  // DDA1: 1 output FAULT
  // DDA0: 1 output en_power
  DDRA &= ~( (1 << PA7) | (1 << PA6) | (1 << PA5) | (1 << PA4) | (1 << PA2) );
  DDRA |=    (1 << PA3) | (1 << PA1) | (1 << PA0);

  // Enable pullups on PA[7] input
  // Enable pullups on PA[6:0] for low-power
  PORTA &= ~( (1 << PA3) | (1 << PA1) ); // first time power, don't want fault or dev-mode asserted
  PORTA |= (1 << PA7) | (1 << PA6) | (1 << PA5) | (1 << PA4) |
           (1 << PA2) | (1 << PA0);

  // DDRB Port Directions
  //
  // DDB3: 0 input RESET_N
  // DDB2: 0 input rtc_ALRM_N
  // DDB1: 0 input psh_button
  // DDB0: 1 DNC low-power
  DDRB &= ~( (1 << PB3) | (1 << PB2) | (1 << PB1) );
  DDRB |=    (1 << PB0);

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

// todo: will an interrupt while another interrupt is being serviced cause contention on en_power??

/*
 * RTC Alarm ISR
 */
ISR(EXT_INT0_vect)
{
  if ~(PINB & (1 << PB2)) // Alarm has occured
  {
    if (PINA & (1 << PA0)) // Checking to see if load switch already on
    {
      // todo: Should FAULTS ever be cleared before user intervention??
      PORTA |= (1 << PA1); // raise FAULT as this shouldn't happen, but maintain power to device
    }
    else
    {
      PORTA |= (1 << PA0); // Turn load switch on
    }
  }
  else //
  {
    // todo: find out if any error checking needs to be done when alarm is cleared
    //       should be branching back to service other interrupts or sleep
  }

  // Insert nop for synchronization
  _NOP();

  // Clear interrupt flag
  GIFR |= (1 << INTF0);
}

/*
 * pi_tx_hold_on ISR
 */
// todo: how to incorporate check for if this condition never happens when push button or
//       RTC alarm event occur??
ISR(PCINT0_vect)
{
  if (PINA & (1 << PA7)) // Pi has turned on
  {
    while ~(PINB & (1 << PB2)) // while alarm not cleared, check until cleared
    {
      // todo: sleep for some time
      // todo: what happens when alarm on INT0 gets cleared? does that get serviced before coming back here?
      // todo: add _WDT(), timer, or variable so we don't get stuck
    }
  }
  else // Pi has turned off
  {
    // todo: sleep here for ~30s-45s and error-check
    if (PINA & (1 << PA0)) // done sleeping, make sure load switch is on
    {
      PORTA &= ~(1 << PA0); // Turn load switch off
    }
    else
    {
      PORTA |= (1 << PA1); // Raise FAULT as this should never happen
    }
    PORTA &= ~(1 << PA3); // Turn dev mode off
  }

  // Insert nop for synchronization
  _NOP();

  // Clear interrupt flag
  GIFR |= (1 << PCIF0);
}

/*
 * Push Button ISR
 */
// __debounced in analog__
ISR(PCINT1_vect)
{
  // todo: sleep debounce alg here to remove res/cap
  if ~(PINB & (1 << PB1)) // seeing dev-mode req
  {
    if ~(PINA & (1 << PA0)) // if power is off, turn it on
    {
      PORTA |= (1 << PA0);
    } // else do nothing
    PORTA |= (1 << PA3); // assert dev mode
  }
  // else do nothing

  // Insert nop for synchronization
  _NOP();

  // Clear interrupt flag
  GIFR |= (1 << PCIF1);
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

