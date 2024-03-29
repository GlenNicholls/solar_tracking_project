#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/power.h>
#include <avr/sleep.h>
#include <avr/cpufunc.h>  // for _NOP()



/*****************************
 * Function Prototypes
 *****************************/
// todo: should all these be defined here or elsewhere??
// static inline void initWDT(void);
static inline void initClock          (void);
static inline void initTimer0         (void);
static inline void initTimer1         (void);
static inline void startDebounceTimer (void);
static inline void stopDebounceTimer  (void);
static inline void startBigTimer      (void);
static inline void stopBigTimer       (void);
static inline void initInterrupts     (void);
static inline void initLowPower       (void);
static inline void disableAllTimers   (void);
static inline void enableAllTimers    (void);

static inline void initPortA             (void);
static inline void initPortB             (void);
static inline void setPinStartupState    (void);
static inline int powerIsOn              (void);
static inline int faultIsOn              (void);
static inline int devModeIsOn            (void);
static inline int deviceAckIsOn          (void);
static inline int buttonIsOn             (void);
static inline int rtcAlarmIsOn           (void);
static inline int powerFlagIsSet         (void);
static inline int faultFlagIsSet         (void);
static inline int devModeFlagIsSet       (void);
static inline int checkAlarmFlagIsSet    (void);
static inline int shutdownDelayFlagIsSet (void);
static inline int checkAckFlagIsSet      (void);
static inline int timer0IsOn             (void);
static inline int timer1IsOn             (void);

static inline void initMCU             (void);
static inline void serviceGpioRegFlags (void);
static inline void goToSleep           (void);



/*****************************
 * Bit/Reg Manipulation Macros
 *****************************/
#define SET_BIT(PORT, BIT) ( PORT |=  _BV(BIT) )
#define CLR_BIT(PORT, BIT) ( PORT &= ~_BV(BIT) )
#define TGL_BIT(PORT, BIT) ( PORT ^=  _BV(BIT) )

#define SET_OUTPUT(DDRX, BIT) ( DDRX |=  _BV(BIT) )
#define SET_INPUT(DDRX, BIT)  ( DDRX &= ~_BV(BIT) )

#define SET_PULLUP_ON(PORT, BIT)  ( PORT |=  _BV(BIT) )
#define SET_PULLUP_OFF(PORT, BIT) ( PORT &= ~_BV(BIT) )

#define SET_BITS(REG, VAL, BASE) ( REG |=  (VAL << BASE) )
#define CLR_BITS(REG, VAL, BASE) ( REG &= ~(VAL << BASE))

#define SET_REG(REG, VAL) (REG = VAL)



/*****************************
 * Timer Prescalars
 *****************************/
#define TIMER_OFF            0b000
#define TIMER_PRESCALE_1     0b001
#define TIMER_PRESCALE_8     0b010
#define TIMER_PRESCALE_64    0b011
#define TIMER_PRESCALE_256   0b100
#define TIMER_PRESCALE_1024  0b101
#define TIMER_ON_MASK        0b111



/*****************************
 * Clock Config Macros
 *****************************/
// todo: possibly use CKSEL to choose different clock
#ifndef F_CPU
#error You must define F_CPU
#else
  // not supporting any higher freqs since this would require global counter
  // this is also supposed to be low power, so those freqs are pointless
  #if (F_CPU == 2000000)
    #define CLOCK_DIV         clock_div_4
    #define TIMER_0_PRESCALE  TIMER_PRESCALE_256
    #define TIMER_1_PRESCALE  TIMER_PRESCALE_1024
    #define TIMER_0_OCRA      250
    #define TIMER_1_OCRA      65535
    #define TIMER_1_OCRB      6000

  #elif (F_CPU == 1000000)
    #define CLOCK_DIV         clock_div_8
    #define TIMER_0_PRESCALE  TIMER_PRESCALE_256
    #define TIMER_1_PRESCALE  TIMER_PRESCALE_1024
    #define TIMER_0_OCRA      130
    #define TIMER_1_OCRA      40000
    #define TIMER_1_OCRB      3000

  #elif (F_CPU == 500000)
    #define CLOCK_DIV         clock_div_16
    #define TIMER_0_PRESCALE  TIMER_PRESCALE_64
    #define TIMER_1_PRESCALE  TIMER_PRESCALE_1024
    #define TIMER_0_OCRA      250
    #define TIMER_1_OCRA      20000
    #define TIMER_1_OCRB      1500

  #elif (F_CPU == 250000)
    #define CLOCK_DIV         clock_div_32
    #define TIMER_0_PRESCALE  TIMER_PRESCALE_64
    #define TIMER_1_PRESCALE  TIMER_PRESCALE_1024
    #define TIMER_0_OCRA      130
    #define TIMER_1_OCRA      10000
    #define TIMER_1_OCRB      750

  #elif (F_CPU == 125000)
    #define CLOCK_DIV         clock_div_64
    #define TIMER_0_PRESCALE  TIMER_PRESCALE_64
    #define TIMER_1_PRESCALE  TIMER_PRESCALE_1024
    #define TIMER_0_OCRA      70
    #define TIMER_1_OCRA      5000
    #define TIMER_1_OCRB      375

  #elif (F_CPU == 62500)
    #define CLOCK_DIV         clock_div_128
    #define TIMER_0_PRESCALE  TIMER_PRESCALE_8
    #define TIMER_1_PRESCALE  TIMER_PRESCALE_1024
    #define TIMER_0_OCRA      250
    #define TIMER_1_OCRA      2500
    #define TIMER_1_OCRB      185

  #elif (F_CPU == 31250)
    #define CLOCK_DIV         clock_div_256
    #define TIMER_0_PRESCALE  TIMER_PRESCALE_8
    #define TIMER_1_PRESCALE  TIMER_PRESCALE_256
    #define TIMER_0_OCRA      130
    #define TIMER_1_OCRA      5000
    #define TIMER_1_OCRB      750

  #else
    #error Unsupported value for F_CPU
  #endif
#endif

static inline void initClock(void)
{
  //clock_prescale_set(clock_div_64); // yields 125kHz clk
  clock_prescale_set(CLOCK_DIV);

  // synchronize
  _NOP();
}



/*****************************
 * Timer Config Macros
 *****************************/
#define TIMER_0_WGM_NORMAL  0b10 // todo: possibly add more but probably don't need now
#define TIMER_0_WGM_CTC     0b10

// todo: devise better way for WGM here since we have to write 2 regs
#define TIMER_1_WGM_REG1_NORMAL  0b00
#define TIMER_1_WGM_REG2_NORMAL  0b00
#define TIMER_1_WGM_REG1_CTC     0b00
#define TIMER_1_WGM_REG2_CTC     0b01

#define SET_TIMER_0_MODE_NORMAL SET_BITS(TCCR0A, TIMER_0_WGM_NORMAL, WGM00)
#define SET_TIMER_0_MODE_CTC    SET_BITS(TCCR0A, TIMER_0_WGM_CTC, WGM00)
#define CLR_TIMER_0_COUNT       SET_REG(TCNT0, 0x00)
#define TURN_TIMER_0_ON         SET_BITS(TCCR0B, TIMER_0_PRESCALE, CS00)
#define TURN_TIMER_0_OFF        CLR_BITS(TCCR0B, ~TIMER_OFF, CS00) // todo: how do I make this generic for the prescalar and output compare reg??

#define SET_TIMER_1_REG1_MODE_NORMAL SET_BITS(TCCR1A, TIMER_1_WGM_REG1_NORMAL, WGM10)
#define SET_TIMER_1_REG2_MODE_NORMAL SET_BITS(TCCR1B, TIMER_1_WGM_REG2_NORMAL, WGM12)
#define SET_TIMER_1_REG1_MODE_CTC    SET_BITS(TCCR1A, TIMER_1_WGM_REG1_CTC, WGM10)
#define SET_TIMER_1_REG2_MODE_CTC    SET_BITS(TCCR1B, TIMER_1_WGM_REG2_CTC, WGM12)
#define CLR_TIMER_1_COUNT            SET_REG(TCNT1, 0x0000) // tcnt1 gives direct access to both regs
#define TURN_TIMER_1_ON              SET_BITS(TCCR1B, TIMER_1_PRESCALE, CS10)
#define TURN_TIMER_1_OFF             CLR_BITS(TCCR1B, ~TIMER_OFF, CS10)

// 8-bit timer
static inline void initTimer0(void)
{
  // Clear timer on compare match
  SET_TIMER_0_MODE_CTC;

  // Make sure it isn't free-running
  TURN_TIMER_0_OFF;
  CLR_TIMER_0_COUNT;

  // Enable compare match INT
  TIMSK0 |= _BV(OCIE0A);
}

// 16-bit timer
static inline void initTimer1(void)
{
  // Clear timer on compare match
  SET_TIMER_1_REG1_MODE_NORMAL;
  SET_TIMER_1_REG2_MODE_NORMAL;

  // Make sure it isn't free-running
  TURN_TIMER_1_OFF;
  CLR_TIMER_1_COUNT;

  // Enable compare match INT
  TIMSK1 |= _BV(OCIE1A); // flag for startup/shutdown
  TIMSK1 |= _BV(OCIE1B); // flag for clearing FAULT
}

// 8-bit timer
// todo: how to make this generic
// spec of push button is 13ms, added some slack to be safe
// 1/( (F_CPU/prescale) /(2*prescale*(1 + timer_count_to))) = 36.9ms
static inline void startDebounceTimer(void)
{
  // 1/(F_CPU/(2*prescale*(1 + timer_compare))) = ~37ms

  // Output compare reg
  OCR0A = TIMER_0_OCRA;

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

// 16-bit timer
static inline void startBigTimer(void)
{
  // 1/(F_CPU/(prescale*(1 + timer_compare)))

  // Output compare reg
  OCR1A = TIMER_1_OCRA; // ~41s wait for startup/shutdown
  OCR1B = TIMER_1_OCRB; // ~3s wait for clearing FAULT

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
 * Interrupt Config Macros
 *****************************/
#define INT0_MODE_LOGIC_CHANGE 0b01
//#define SLEEP_MODE_IDLE        0b00
//#define SLEEP_MODE_PWR_DOWN    0b10
//#define SLEEP_MODE_STAND_BY    0b11

static inline void initInterrupts(void)
{
  // Configure INT0 interrupt mode
  SET_BITS(MCUCR, INT0_MODE_LOGIC_CHANGE, ISC00);

  // General Interrupt Mask Register
  GIMSK |= _BV(PCIE0) | _BV(PCIE1);

  // Pin Change Mask Registers
  PCMSK0 |= _BV(PCINT7);
  PCMSK1 |= _BV(PCINT9);
  PCMSK1 |= _BV(PCINT10);
}



/*****************************
 * WDT Config Macros
 *****************************/
// todo: should the init functions be put into a .h as well??
// todo: implement this when the time comes
// static inline void WDT_off(void)
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


/*****************************
 * Low-Pwr/Sleep Config Macros
 *****************************/
// todo: might be beneficial to disable timers when not used. can enable them in the
//       turn on functions
static inline void initLowPower(void)
{
  // Disable ADC
  power_adc_disable();

  // Disable analog comparator
  ACSR |= _BV(ACD);

  // Disable USI
  power_usi_disable();
}

static inline void disableAllTimers(void)
{
  power_timer0_disable();
  power_timer1_disable();
}

static inline void enableAllTimers(void)
{
  power_timer0_enable();
  power_timer1_enable();
}
