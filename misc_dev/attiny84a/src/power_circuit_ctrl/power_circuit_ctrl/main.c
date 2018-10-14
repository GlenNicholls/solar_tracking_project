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
 *        todo: solidify whether pi will be off during the day as this may influence
 *        the algorithm and checks during this stage!
 *
 *        1. This pin is normally pulled high
 *        2. Push button is debounced externally
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
 *        6. During this FAULT condition, the uC will NOT enter a low-power sleep to wait
 *           for an interrupt, it will continue to hold this pin high and will pseudo-
 *           take over for the RTC.
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
 *           user specifies it do so.
 */

#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>


#define F_CPU 8000000
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


// todo: Complete GIFR ISR Routines


int main(void)
{
    // Configure DDRA Port Directions
    //
    // DDA7: 1 input pi_tx_hold_on PCINT7
    // DDA6: 0 DNC low-pwr
    // DDA5: 0 DNC low-pwr
    // DDA4: 0 DNC low-pwr
    // DDA3: 0 output pi_rx_dev_mode
    // DDA2: 0 DNC low-pwr
    // DDA1: 0 FAULT output
    // DDA0: 0 output en_power
    DDRA |= (1 << PA7);
    DDRA &= ~( (1 << PA6) | (1 << PA5) | (1 << PA4) | (1 << PA3) |
               (1 << PA2) | (1 << PA1) | (1 << PA0) );


    // Configure DDRB Port Directions
    //
    // DDB3: 0 DNC low-pwr
    // DDB2: 1 input rtc_ALRM_N
    // DDB1: 1 input psh_button
    // DDB0: 0 DNC low-pwr
    DDRB |= (1 << PB2) | (1 << PB1);


    // PB1 (PCINT9 on PCIE1) : active low input from DS3231
    // PB2 (INT0)            : active low input from push button (debounced in analog)



    // Configure the General Interrupt Mask Register
    //
    // PCIE1 : 1 Enable pin change INT
    // PCIE0 : 1 Enable pin change INT
    // INT0  : 1 Enable external interrupt
    // and set I-bit in SREG to one
    GIMSK |= (1 << INT0) | (1 << PCIE0) | (1 << PCIE1);
    sei();


    // Configure the Pin Change Mask Registers
    //
    // Enable specific pin change interrupts in the
    // pin change mask reg
    PCMSK0 |= (1 << PCINT7);
    PCMSK1 |= (1 << PCINT9);


    // Configure MCU Control Register
    //
    // BODS  : disable BOD during low-power?
    // PUD   : ??
    // SE    : 1 Enable sleep enable
    // SM1   : 1
    // SM0   : 1 Enable standby sleep mode
    // ISC00 : 1
    // ISC01 : 0 Any INT0 level change generates INT
    // BODSE : ??
    // todo: would power-down be better since it halts clocks and only wakes on async events??
    // todo: should SE only be enabled when desired and cleared upon wakeup??
    MCUCR |=  (1 << SE) | (1 << SM1) | (1 << SM0) | (1 << ISC00);
    MCUCR &= ~(1 << ISC01);


    // Configure the Power Reduction Register
    //
    // PRTIM1 : ??
    // PRTIM0 : ??
    // PRUSI  : ??
    // PRADC  : 1 to disable ADC
    PRR |= (1 << PRADC);


    // Configure Analog Comparator Control/Status Register
    //
    // ACD: 1 switch off analog comparator
    ACSR |= (1 << ACD);


    while (1)
    {
        sleep();
        //_delay_ms(200);
    }
}

