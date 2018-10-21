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

#include <pi_hat_ctrl.h>


// todo: should the init functions be put into a .h as well??
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

// todo: set full register if need memory
// todo: put all hardware specific in attiny84a.h
// todo: figure out best dir/pullup state for low-power on not connected pins
static inline void initPortA(void)
{
  // DDRA Port Directions
  SET_INPUT(DDRA, DEVICE_ACK_PIN_REG);
  SET_INPUT(DDRA, ISCP_MOSI);
  SET_INPUT(DDRA, ISCP_MISO);
  SET_INPUT(DDRA, ISCP_SCK);
  SET_INPUT(DDRA, PA2); // not connected

  SET_OUTPUT(DDRA, DEV_MODE_PIN_REG);
  SET_OUTPUT(DDRA, FAULT_PIN_REG);
  SET_OUTPUT(DDRA, POWER_PIN_REG);

  // Enable pullups
  SET_PULLUP_ON(PORTA, DEVICE_ACK_PIN_REG);
  SET_PULLUP_ON(PORTA, ISCP_MOSI);
  SET_PULLUP_ON(PORTA, ISCP_MISO);
  SET_PULLUP_ON(PORTA, ISCP_SCK);
  SET_PULLUP_ON(PORTA, PA2); // not connected
  SET_PULLUP_ON(PORTA, POWER_PIN_REG);

  SET_PULLUP_OFF(PORTA, DEV_MODE_PIN_REG); // don't want enabled when first powered on
  SET_PULLUP_OFF(PORTA, FAULT_PIN_REG);    // don't want enabled when first powered on
}

static inline void initPortB(void)
{
  // DDRB Port Directions
  SET_INPUT(DDRB, ICSP_RESET_N);
  SET_INPUT(DDRB, RTC_ALARM_PIN_REG);
  SET_INPUT(DDRB, BUTTON_PIN_REG);

  SET_OUTPUT(DDRB, PB0); // not connected

  // Enable pullups
  SET_PULLUP_ON(PORTB, ICSP_RESET_N);
  SET_PULLUP_ON(PORTB, RTC_ALARM_PIN_REG);
  SET_PULLUP_ON(PORTB, BUTTON_PIN_REG);
  SET_PULLUP_ON(PORTB, PB0); // not connected
}

// todo: abstract this in .h
static inline void initInterrupts(void)
{
  // Configure INT0 interrupt mode
  SET_BITS(MCUCR, LOGIC_CHANGE, ISC00);

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

// Configure timer(s)
// F_CPU/(prescaler*(1 + OCR0A)) = F_num_timer_OVF

// 8-bit timer
// todo: configure longer timer for ~10s to turn off dev-mode
//       the short mode below is to debounce the button to turn on
//       dev mode... To do this, timer needs to be normal mode to rollover at 0xFF
// todo: 16-bit timer for big honking times!
static inline void initTimer0(void)
{
  // Clear timer on compare match
  // com0XX just affects this pin, so don't touch right??
  SET_TIMER_0_MODE_CTC;

  // Make sure it isn't free-running
  TURN_TIMER_0_OFF;

  // Enable compare match INT
  // todo: overflow INT TOIE0??
  TIMSK0 |= (1 << OCIE0A);
}

// todo: how to make this generic
static inline void startDebounceTimer(void)
{
  // Output compare reg
  // todo: put in specific function for configuring correct period
  OCR0A = 50; // 8M/(2*1024(1+50)) = 77Hz = 12ms... It's Gr8!!!

  // Activate timer with prescalar 1024
  TURN_TIMER_0_ON;
}

static inline void stopDebounceTimer(void)
{
  // Disable timer
  TURN_TIMER_0_OFF;
}

// configure clocks
// static inline initClocks(void)
// {
//   // todo: not sure how to configure clocks yet
// }

// configure low-power
// todo: don't shove everything in single function, pull stuff to other functions
//       to make code clearer
// static inline initLowPowerMode(void)
// {
//   // todo: not sure how to configure clocks yet
//
//   // Analog Comparator Control/Status Register
//   ACSR |= (1 << ACD); // disable
//
//   // Power Reduction Register
//   //
//   // PRTIM1 : ??
//   // PRTIM0 : ??
//   // PRUSI  : ??
//   PRR |= (1 << PRADC); // disable ADC
//
//   // Sleep Mode
//   //
//   // BODS  : disable BOD during low-power?
//   // PUD   : ??
//   // BODSE : ??
//   // todo: would power-down be better since it halts clocks and only wakes on async events??
//   // todo: should SE only be enabled when desired and cleared upon wakeup??
//   MCUCR |= (1 << SE);     // Enable sleep
//   MCUCR |= (0b11 << SM0); // Mode: standby
// }

static inline void initMCU(void)
{
  // init directions and pullups on port A
  initPortA();

  // init directions and pullups on port B
  initPortB();

  // Enable the MCUCR pullups
  MCUCR &= ~(1 << PUD);

  // Configure INT
  initInterrupts();

  // Configure clocks
//  initClocks()
  // Configure low-power mode
//  initLowPowerMode();

  // Enable global interrupts by set I-bit in SREG to 1
  sei();
}

// todo: implicit mutex using function for error checking



// /*
//  * RTC Alarm ISR
//  */
// ISR(EXT_INT0_vect)
// {
//   if (rtcAlarmIsOn()) // Alarm has occured
//   {
//     if (powerIsOn()) // Checking to see if load switch already on
//     {
//       // todo: Should FAULTS ever be cleared before user intervention??
//       TURN_FAULT_ON; // raise FAULT as this shouldn't happen, but maintain power to device
//     }
//     else
//     {
//       TURN_POWER_ON; // Turn load switch on
//     }
//   }
//   // todo: find out if any error checking needs to be done when alarm is cleared
//   //       should be branching back to service other interrupts or sleep
//   // else {}
//
//   // Insert nop for synchronization
//   _NOP();
// }

/*
 * pi_tx_hold_on ISR
 */
// todo: how to incorporate check for if this condition never happens when push button or
//       RTC alarm event occur??
ISR(PCINT0_vect)
{
  if (deviceAckIsOn()) // Pi has turned on
  {
    // while (isRTCAlarmOn()) // while alarm not cleared, check until cleared
    // {
    //   // todo: sleep for some time
    //   // todo: what happens when alarm on INT0 gets cleared? does that get serviced before coming back here?
    //   // todo: add _WDT(), timer, or variable so we don't get stuck
    // }
  }
  else // Pi has turned off
  {
    // todo: start timer1 here for ~30s-45s and error-check
    if (powerIsOn()) // done sleeping, make sure load switch is on
    {
      TURN_POWER_OFF; // Turn load switch off
    }
    else
    {
      TURN_FAULT_ON; // Raise FAULT as this should never happen
    }
    TURN_DEV_MODE_OFF; // Turn dev mode off
  }

  // Insert nop for synchronization
  _NOP();
}

/*
 * Push Button ISR
 */
// todo: * when we enter, start timer if not already started.
//       * let timer ISR take care of all logic to set the device reg for big func
ISR(PCINT1_vect)
{
  // todo: check flag register to see if dev mode is on, then put
  //       logic in here to account for when to start debounce timer
  if (buttonIsOn()) // seeing dev mode req
  {
    if (~timer0IsOn()) // if timer is alreay on we're going, "hey, wire"!!!
    {
      startDebounceTimer();
    }
  }

  // Insert nop for synchronization
  _NOP();
}



// todo: test code below
/////////////////////////////////////////////////////////// TEST CODE
ISR(EXT_INT0_vect)                                       // TEST CODE
{                                                        // TEST CODE
  if (rtcAlarmIsOn()) // Alarm has occured               // TEST CODE
  {                                                      // TEST CODE
    SET_POWER_FLAG; // Turn load switch on               // TEST CODE
  }                                                      // TEST CODE
  else                                                   // TEST CODE
  {                                                      // TEST CODE
    CLR_POWER_FLAG;                                      // TEST CODE
  }                                                      // TEST CODE
                                                         // TEST CODE
  // Insert nop for synchronization                      // TEST CODE
  _NOP();                                                // TEST CODE
}                                                        // TEST CODE
/////////////////////////////////////////////////////////// TEST CODE

/*
 * Timer 0 Compare A ISR
 */
ISR(TIM0_COMPA_vect)
{
  // todo: for all ISRs, will be checking pin states, not flags. Flag checking is
  //       taken care of by func in main. This is safe because interrupts will be
  //       disabled when entering func, and enabled when leaving.
  // todo: not adding forced shutdown as this could mean that an alarm isn't set
  //       and the pi would never wake up. Would be complicated to play games to
  //       also schedule some variation of fault/dev mode to denote this for pi.
  // if power is off and button pressed, turn power on and enter dev mode
  // if power is on and button is pressed, leave power on and check dev mode
  //    if dev mode is active, deactivate. else turn dev mode on
  if (powerIsOn())
  {
    // todo: toggling flag should be safe as long as we're properly debounced. will
    //       be testing with scope on friday
    if (devModeIsOn())
    {
      CLR_DEV_MODE_FLAG;
    }
    else
    {
      SET_DEV_MODE_FLAG;
    }
  }
  else
  {
    SET_POWER_FLAG;
    SET_DEV_MODE_FLAG;
  }

  // Disable timer now as it has served heroically
  stopDebounceTimer();

  // Insert nop for synchronization
  _NOP();
}

// todo: will be making this more much better later
static inline void serviceGpioRegFlags(void)
{
  // disable interrupts to prevent flags changing
  cli();

  if (powerFlagIsSet())
  {
    TURN_POWER_ON;
  }
  if (faultFlagIsSet())
  {
    TURN_FAULT_ON;
  }
  if (devModeFlagIsSet())
  {
    TURN_DEV_MODE_ON;
  }

  // re-enable interrupts
  sei();
}


int main(void)
{
  initMCU();

  while (1)
  {
    serviceGpioRegFlags();
    //sleep_cpu();
  }

  return 0;
}

