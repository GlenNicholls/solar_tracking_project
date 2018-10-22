#include <avr/io.h>
#include <avr/interrupt.h>
//#include <avr/sfr_defs.h> // io should include this
#include <avr/power.h>
#include <avr/sleep.h>

// used for a very short delay
#define _NOP() do { __asm__ __volatile__ ("nop"); } while (0)

// todo: Where are these macros defined??
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
  Off      = 0b000,
  Div_1    = 0b001,
  Div_8    = 0b010,
  Dev_64   = 0b011,
  Dev_256  = 0b100,
  Dev_1024 = 0b101
} timerPrescaleT;
#define TIMER_OFF              0b000
#define TIMER_PRESCALE_1       0b001
#define TIMER_PRESCALE_8       0b010
#define TIMER_PRESCALE_64      0b011
#define TIMER_PRESCALE_256     0b100
#define TIMER_PRESCALE_1024    0b101
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
#define TURN_TIMER_0_ON         SET_BITS(TCCR0B, TIMER_PRESCALE_1024, CS00)
#define TURN_TIMER_0_OFF        CLR_BITS(TCCR0B, ~TIMER_OFF, CS00) // todo: how do I make this generic for the prescalar and output compare reg??

#define SET_TIMER_1_REG1_MODE_NORMAL SET_BITS(TCCR1A, TIMER_1_WGM_REG1_NORMAL, WGM10)
#define SET_TIMER_1_REG2_MODE_NORMAL SET_BITS(TCCR1B, TIMER_1_WGM_REG2_NORMAL, WGM12)
#define SET_TIMER_1_REG1_MODE_CTC    SET_BITS(TCCR1A, TIMER_1_WGM_REG1_CTC, WGM10)
#define SET_TIMER_1_REG2_MODE_CTC    SET_BITS(TCCR1B, TIMER_1_WGM_REG2_CTC, WGM12)
#define CLR_TIMER_1_COUNT            SET_REG(TCNT1, 0x0000) // tcnt1 gives direct access to both regs
#define TURN_TIMER_1_ON              SET_BITS(TCCR1B, TIMER_PRESCALE_1024, CS10)
#define TURN_TIMER_1_OFF             CLR_BITS(TCCR1B, ~TIMER_OFF, CS10)


// INT values
#define LOGIC_CHANGE 0b01


// define pins for readability
#define POWER_PIN_REG      PA0
#define FAULT_PIN_REG      PA1
#define DEV_MODE_PIN_REG   PA3
#define ISCP_SCK           PA4
#define ISCP_MISO          PA5
#define ISCP_MOSI          PA6
#define DEVICE_ACK_PIN_REG PA7
#define BUTTON_PIN_REG     PB1
#define RTC_ALARM_PIN_REG  PB2
#define ICSP_RESET_N       PB3

#define POWER_PORT      PORTA
#define FAULT_PORT      PORTA
#define DEV_MODE_PORT   PORTA
#define DEVICE_ACK_PORT PORTA
#define BUTTON_PORT     PORTB
#define RTC_ALARM_PORT  PORTB

#define POWER_PIN      PINA
#define FAULT_PIN      PINA
#define DEV_MODE_PIN   PINA
#define DEVICE_ACK_PIN PINA
#define BUTTON_PIN     PINB
#define RTC_ALARM_PIN  PINB

#define POWER_STATUS_MASK      _BV(POWER_PIN_REG)
#define FAULT_STATUS_MASK      _BV(FAULT_PIN_REG)
#define DEV_MODE_STATUS_MASK   _BV(DEV_MODE_PIN_REG)
#define DEVICE_ACK_STATUS_MASK _BV(DEVICE_ACK_PIN_REG)
#define BUTTON_STATUS_MASK     _BV(BUTTON_PIN_REG)
#define RTC_ALARM_STATUS_MASK  _BV(RTC_ALARM_PIN_REG)

// todo: this should all only be used in function inside main
// todo: possibly change to toggling?
#define TURN_POWER_ON      SET_BIT(POWER_PORT,    POWER_PIN_REG)
#define TURN_POWER_OFF     CLR_BIT(POWER_PORT,    POWER_PIN_REG)
#define TURN_FAULT_ON      SET_BIT(FAULT_PORT,    FAULT_PIN_REG)
#define TURN_FAULT_OFF     CLR_BIT(FAULT_PORT,    FAULT_PIN_REG)
#define TURN_DEV_MODE_ON   SET_BIT(DEV_MODE_PORT, DEV_MODE_PIN_REG)
#define TURN_DEV_MODE_OFF  CLR_BIT(DEV_MODE_PORT, DEV_MODE_PIN_REG)


// GPIO register macros
#define GPIOR2_POWER_FLAG_REG    7
#define GPIOR2_FAULT_FLAG_REG    6
#define GPIOR2_DEV_MODE_FLAG_REG 5

#define GPIOR2_POWER_FLAG_MASK    _BV(GPIOR2_POWER_FLAG_REG)
#define GPIOR2_FAULT_FLAG_MASK    _BV(GPIOR2_FAULT_FLAG_REG)
#define GPIOR2_DEV_MODE_FLAG_MASK _BV(GPIOR2_DEV_MODE_FLAG_REG)

#define SET_POWER_FLAG     loop_until_bit_is_set(GPIOR2, GPIOR2_POWER_FLAG_REG)
#define CLR_POWER_FLAG     loop_until_bit_is_clear(GPIOR2, GPIOR2_POWER_FLAG_REG)
#define SET_FAULT_FLAG     loop_until_bit_is_set(GPIOR2, GPIOR2_FAULT_FLAG_REG)
#define CLR_FAULT_FLAG     loop_until_bit_is_clear(GPIOR2, GPIOR2_FAULT_FLAG_REG)
#define TGL_DEV_MODE_FLAG  TGL_BIT(GPIOR2, GPIOR2_DEV_MODE_FLAG_REG)
#define SET_DEV_MODE_FLAG  loop_until_bit_is_set(GPIOR2, GPIOR2_DEV_MODE_FLAG_REG)
#define CLR_DEV_MODE_FLAG  loop_until_bit_is_clear(GPIOR2, GPIOR2_DEV_MODE_FLAG_REG)



// functions for checking pin states
// todo: where to put these??
static inline int powerIsOn(void)
{
  return bit_is_set(POWER_PIN, POWER_STATUS_MASK);
}

static inline int powerFlagIsSet(void)
{
  return bit_is_set(GPIOR2, GPIOR2_POWER_FLAG_MASK);
}

static inline int faultIsOn(void)
{
  return bit_is_set(FAULT_PIN, FAULT_STATUS_MASK);
}

static inline int faultFlagIsSet(void)
{
  return bit_is_set(GPIOR2, GPIOR2_FAULT_FLAG_MASK);
}

static inline int devModeIsOn(void)
{
  return bit_is_set(DEV_MODE_PIN, DEV_MODE_STATUS_MASK);
}

static inline int devModeFlagIsSet(void)
{
  return bit_is_set(GPIOR2, GPIOR2_DEV_MODE_FLAG_MASK);
}

static inline int deviceAckIsOn(void)
{
  return bit_is_set(DEVICE_ACK_PIN, DEVICE_ACK_STATUS_MASK);
}

static inline int buttonIsOn(void) // look for low-going edge (active low)
{
  return bit_is_clear(BUTTON_PIN, BUTTON_STATUS_MASK);
}

static inline int rtcAlarmIsOn(void) // look for low-going edge (active low)
{
  return bit_is_clear(RTC_ALARM_PIN, RTC_ALARM_STATUS_MASK);
}

static inline int timer0IsOn(void)
{
  return bit_is_set(TCCR0B, TIMER_ON_MASK);
}


static inline int timer1IsOn(void)
{
  return bit_is_set(TCCR1B, TIMER_ON_MASK);
}

// function prototypes or whatever it's called here
static inline void initPortA(void);
static inline void initPortB(void);
static inline void initInterrupts(void);
static inline void initMCU(void);
static inline void startDebounceTimer(void);
static inline void stopDebounceTimer(void);
static inline void serviceGpioRegFlags(void);

