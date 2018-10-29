/*
 * main.c
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
 *    TODO: Get rid of this junk and make a flow chart instead. This will be clearer
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
 *        1. This pin is normally pulled high
 *        2. When there is a low-going edge, an interrupt will be issued.
 *        3. After device on, RTC alarm should be cleared and then ack raised.
 *        4. if RTC alarm is not cleared before this, fault will be raised.
 *        5. If device is originally off, dev mode pin is asserted and power turned
 *           on.
 *        6. If device is on, dev mode pin asserted until user presses button again
 *
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


/*****************************
 * Global
 *****************************/
//void int checkFaultFlag = 0; // to periodically check fault flag to see if we need to forcefully turn on pi.


/*****************************
 * 8-Bit Timer Helpers
 *****************************/
// todo: how to make this generic
// spec of push button is 13ms, added some slack to be safe
// 1/(125000/(2*8*(1 + 35))) = 36.9ms
static inline void startDebounceTimer(void)
{
  // 1/(125000/(2*8*(1 + 35))) = ~37ms

  // Output compare reg
  OCR0A = 35;

  // Activate timer with prescalar 8
  TURN_TIMER_0_ON;
}

static inline void stopDebounceTimer(void)
{
  // Disable timer
  TURN_TIMER_0_OFF;

  // Clear timer counter
  CLR_TIMER_0_COUNT;
}


/*****************************
 * 16-Bit Timer Helpers
 *****************************/
static inline void startBigTimer(void)
{
  // 1/(125000/(1024*(1 + 5000))) = ~41s

  // Output compare reg
  //OCR1A = 2000;// DBG
  OCR1A = 5000;

  // Activate timer with prescalar 1024
  TURN_TIMER_1_ON;
}

static inline void stopBigTimer(void)
{
  // Disable timer
  TURN_TIMER_1_OFF;

  // Clear timer counter
  CLR_TIMER_1_COUNT;
}


/*****************************
 * Initialize MCU
 *****************************/
static inline void initMCU(void)
{
  // init pin directions and pullups
  initPortA();
  initPortB();

  // Set start-up state when uC first gets power
  // todo: fix start up glitch when uC sees first alarm after power on
  // todo: add clear all GPIO flags or something
  setPinStartupState();

  // Configure all interrupts
  initInterrupts();
  initTimer0();
  initTimer1();

  // Configure clocks
  initClock();

  // Configure low-power mode
  initLowPower();

  // Enable interrupts
  sei();
}


/*****************************
 * Device Ack ISR
 *****************************/
ISR(PCINT0_vect)
{
  if (!deviceAckIsOn()) // pi has shutdown
  {
    // todo: not sure if we should still shutdown during this fault condition or not
    if (devModeIsOn()) // pi should not be able to shut down with this pin high!
    {
      SET_FAULT_FLAG;
    }

    SET_SHUTDOWN_DLY_FLAG;

    // start timer
    if (!timer1IsOn())
    {
      startBigTimer();
    }
  } // don't check when it comes on since RTC ISR takes care of this
}


/*****************************
 * Push Button ISR
 *****************************/
ISR(PCINT1_vect)
{
  if (!timer0IsOn() && buttonIsOn()) // if timer is alreay on, bounce is going, "hey, wire"
  {
    startDebounceTimer();
  }
}


/*****************************
 * RTC Alarm ISR
 *****************************/
ISR(EXT_INT0_vect)
{
  if (rtcAlarmIsOn()) // Alarm has occured
  {
    // Turn load switch on
    SET_POWER_FLAG;

    // Set flag to check for cleared alarm
    // when timer is done, this should be cleared and ack should be high
    SET_ALARM_CHECK_FLAG;

    // start timer to ensure pi clears this in time
    if (!timer1IsOn())
    {
      startBigTimer();
    }
  } // don't check when it is cleared since timer ISR takes care of this

  _NOP();
}


/*****************************
 * Timer 0 Compare A ISR
 *****************************/
ISR(TIM0_COMPA_vect) // Debounce timer
{
  if (buttonIsOn())
  {
    if (powerIsOn())
    {
      // todo: toggling flag should be safe as long as we're properly debounced. will
      //       be testing with scope on friday
      TGL_DEV_MODE_FLAG;
    }
    else
    {
      SET_POWER_FLAG;
      SET_DEV_MODE_FLAG;
    }
  }
  else
  {
    // Button was released too quickly or has too much bounce
    SET_FAULT_FLAG;
  }

  // Disable timer now as it has served heroically
  stopDebounceTimer();
}


/*****************************
 * Timer 1 Compare A ISR
 *****************************/
ISR(TIM1_COMPA_vect) // long delay timer for checking RTC and allowing pi to shutdown safely.
{
  if (checkAlarmFlagIsSet()) // Need to check alarm and make sure ack is on
  {
    if (rtcAlarmIsOn())
    {
      // pi needs to clear alarm before giving ack!
      SET_FAULT_FLAG;
    }

    if (!deviceAckIsOn()) // no good, no ack from pi so it took too long to start
    {
      SET_FAULT_FLAG;
    }

    CLR_ALARM_CHECK_FLAG;
  }

  if (shutdownDelayFlagIsSet()) // shutdown delay has passed, time to shut pi down
  {
    CLR_POWER_FLAG;
    CLR_SHUTDOWN_DLY_FLAG;
  }

  if (shutdownDelayFlagIsSet() && checkAlarmFlagIsSet()) // either got here unexpectedly or we are trying to shutdown immediately after we're supposed to be powered on
  {
    // no bueno
    SET_FAULT_FLAG;
    CLR_SHUTDOWN_DLY_FLAG;
    CLR_ALARM_CHECK_FLAG;
  }


  stopBigTimer();
}


/*****************************
 * GPIO Reg Service Routine
 *****************************/
static inline void serviceGpioRegFlags(void)
{
  // disable interrupts to prevent flags changing
  cli();

  // control power pin
  powerFlagIsSet() ? TURN_POWER_PIN_ON : TURN_POWER_PIN_OFF;

  // control fault pin
  faultFlagIsSet() ? TURN_FAULT_PIN_ON : TURN_FAULT_PIN_OFF;

  // control dev mode pin
  devModeFlagIsSet() ? TURN_DEV_MODE_PIN_ON : TURN_DEV_MODE_PIN_OFF;

  // re-enable interrupts
  sei();

  // Add some cycles for allowing interrupts to be processed
  _NOP();
}


/*****************************
 * Sleep Mode Logic
 *****************************/
static inline void goToSleep(void)
{
  if (timer0IsOn() || timer1IsOn()) // go into low-pwr state that allows timer interrupts
  {
    set_sleep_mode(SLEEP_MODE_IDLE);
  }
  else // lowest power mode
  {
    disableAllTimers();
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  }

  // disable BOD
  sleep_bod_disable(); // every time since it gets enabled when woken up

  // enable sleep
  sleep_enable();

  // go into desired sleep mode
  //sleep_mode();
  sleep_cpu();
}


int main(void)
{
  initMCU();

  while (1)
  {
    // // disable interrupts after wake up
    // cli();
    //
    // // disable sleep now that we're awake
    // sleep_disable();
    //
    // // enable timers since we disabled before sleep
    // enableAllTimers();
    //
    // // enable interrupts
    // sei();
    // _NOP();

    // initiate pin states based on device register flags
    serviceGpioRegFlags();


    // go to sleep
    // set_sleep_mode(SLEEP_MODE_IDLE);// DBG
    // sleep_enable();                 // DBG
    // sleep_cpu();                    // DBG

    //goToSleep();
  }

  return 0;
}
