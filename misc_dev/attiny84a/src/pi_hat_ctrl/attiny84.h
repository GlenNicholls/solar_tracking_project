#include <avr/io.h>
#include <avr/interrupt.h>
//#include <avr/sfr_defs.h> // io should include this
#include <avr/power.h>
#include <avr/sleep.h>
#include <avr/cpufunc.h>  // for _NOP()



// used for a very short delay
//#define _NOP() do { __asm__ __volatile__ ("nop"); } while (0)



// function prototypes
// todo: should all these be defined here or elsewhere??
// static inline void initClocks(void);
// static inline void initWDT(void);
static inline void initInterrupts(void);
static inline void initTimer0(void);
static inline void initTimer1(void);
static inline void initLowPowerAndSleep(void);
static inline void initPortA(void);
static inline void initPortB(void);

static inline void initMCU(void);
static inline void startDebounceTimer(void);
static inline void stopDebounceTimer(void);
static inline void startBigTimer(void);
static inline void stopBigTimer(void);
static inline void serviceGpioRegFlags(void);

// todo: is this 32-bit integer or does compiler optimize??
static inline int powerIsOn(void);
static inline int powerFlagIsSet(void);
static inline int faultIsOn(void);
static inline int faultFlagIsSet(void);
static inline int devModeIsOn(void);
static inline int devModeFlagIsSet(void);
static inline int deviceAckIsOn(void);
static inline int buttonIsOn(void);
static inline int rtcAlarmIsOn(void);
static inline int timer0IsOn(void);
static inline int timer1IsOn(void);


// define macros
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



// Timer configuration
// todo: use enum instead
typedef enum
{
  off      = 0b000,
  div_1    = 0b001,
  div_8    = 0b010,
  div_64   = 0b011,
  div_256  = 0b100,
  div_1024 = 0b101
} timerPrescaleT;

timerPrescaleT timerPrescale;

//#define TIMER_OFF              0b000
//#define TIMER_PRESCALE_1       0b001
//#define TIMER_PRESCALE_8       0b010
//#define TIMER_PRESCALE_64      0b011
//#define TIMER_PRESCALE_256     0b100
//#define TIMER_PRESCALE_1024    0b101
#define TIMER_ON_MASK          0b111

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
#define TURN_TIMER_0_ON         SET_BITS(TCCR0B, timerPrescale.div_1024, CS00)
#define TURN_TIMER_0_OFF        CLR_BITS(TCCR0B, ~timerPrescale.off, CS00) // todo: how do I make this generic for the prescalar and output compare reg??

#define SET_TIMER_1_REG1_MODE_NORMAL SET_BITS(TCCR1A, TIMER_1_WGM_REG1_NORMAL, WGM10)
#define SET_TIMER_1_REG2_MODE_NORMAL SET_BITS(TCCR1B, TIMER_1_WGM_REG2_NORMAL, WGM12)
#define SET_TIMER_1_REG1_MODE_CTC    SET_BITS(TCCR1A, TIMER_1_WGM_REG1_CTC, WGM10)
#define SET_TIMER_1_REG2_MODE_CTC    SET_BITS(TCCR1B, TIMER_1_WGM_REG2_CTC, WGM12)
#define CLR_TIMER_1_COUNT            SET_REG(TCNT1, 0x0000) // tcnt1 gives direct access to both regs
#define TURN_TIMER_1_ON              SET_BITS(TCCR1B, timerPrescale.div_1024, CS10)
#define TURN_TIMER_1_OFF             CLR_BITS(TCCR1B, ~timerPrescale.off, CS10)



// general definitions
#define INT0_MODE_LOGIC_CHANGE 0b01
#define SLEEP_MODE_IDLE        0b00
#define SLEEP_MODE_PWR_DOWN    0b10
#define SLEEP_MODE_STAND_BY    0b11



// configuration functions
static inline void initClock(void)
{
  clock_prescale_set(clock_div_64); // yields 125kHz clk

  // synchronize
  _NOP();
}

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

static inline void initInterrupts(void)
{
  // Configure INT0 interrupt mode
  SET_BITS(MCUCR, INT0_MODE_LOGIC_CHANGE, ISC00);

  // General Interrupt Mask Register
  GIMSK |= (1 << INT0) | (1 << PCIE0) | (1 << PCIE1);

  // Pin Change Mask Registers
  PCMSK0 |= (1 << PCINT7);
  PCMSK1 |= (1 << PCINT9);
}

// 8-bit timer
static inline void initTimer0(void)
{
  // F_CPU/(prescaler*(1 + OCR0A)) = F_num_timer_OVF

  // Clear timer on compare match
  SET_TIMER_0_MODE_CTC;

  // Make sure it isn't free-running
  TURN_TIMER_0_OFF;
  CLR_TIMER_0_COUNT;

  // Enable compare match INT
  TIMSK0 |= (1 << OCIE0A);
}

// 16-bit timer
static inline void initTimer1(void)
{
  // 1/(F_CPU/(2*prescaler*(1 + 0xFFFF))) = 16.67s

  // Clear timer on compare match
  SET_TIMER_1_REG1_MODE_NORMAL;
  SET_TIMER_1_REG2_MODE_NORMAL;

  // Make sure it isn't free-running
  TURN_TIMER_1_OFF;
  CLR_TIMER_1_COUNT;

  // Enable compare match INT
  TIMSK0 |= (1 << TOIE1); // will be using globals to check times
}

// configure low-power
// todo: don't shove everything in single function, pull stuff to other functions
//       to make code clearer
// todo: might be beneficial to disable timers when not used. can enable them in the
//       turn on functions
static inline void initLowPowerAndSleep(void)
{
  // Disable ADC
  power_aca_disable();
  power_adc_disable();

  // Disable USI
  power_usi_disable();

  // todo: disable BOD for lower power


  // Sleep Mode
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
  sleep_enable(); // todo: might not need this with sleep_mode();

  //MCUCR |= (1 << SE);     // Enable sleep
  //MCUCR |= (0b11 << SM0); // Mode: standby
}
