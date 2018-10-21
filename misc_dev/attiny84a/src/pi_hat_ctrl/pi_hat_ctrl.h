#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>

// used for a very short delay
#define _NOP() do { __asm__ __volatile__ ("nop"); } while (0)

// todo: where is the header for these things??
// define macros
#define SET_BIT(PORT, BIT) ( PORT |=  (1 << BIT) )
#define CLR_BIT(PORT, BIT) ( PORT &= ~(1 << BIT) )
#define TGL_BIT(PORT, BIT) ( PORT ^=  (1 << BIT) )

#define SET_OUTPUT(DDRX, BIT) ( DDRX |=  (1 << BIT) )
#define SET_INPUT(DDRX, BIT)  ( DDRX &= ~(1 << BIT) )

#define SET_PULLUP_ON(PORT, BIT)  ( PORT |=  (1 << BIT) )
#define SET_PULLUP_OFF(PORT, BIT) ( PORT &= ~(1 << BIT) )

#define SET_BITS(REG, VAL, BASE) ( REG |= (VAL << BASE) )
#define CLR_BITS(REG, VAL, BASE) ( REG &= ~(VAL << BASE))

// todo: MACRO THAT WORKS GOES HERE
#define GET_PIN_STATUS(PIN, MASK) (PIN & MASK)


// Timer configuration
#define TIMER_OFF              0b000
#define TIMER_PRESCALE_1       0b001
#define TIMER_PRESCALE_8       0b010
#define TIMER_PRESCALE_64      0b011
#define TIMER_PRESCALE_256     0b100
#define TIMER_PRESCALE_1024    0b101
#define TIMER_ON_MASK          0b111

#define TIMER_0_WGM_BASE         WGM00
#define TIMER_0_WGM_MODE_NORMAL  0b10 // todo: possibly add more but probably don't need now
#define TIMER_0_WGM_MODE_CTC     0b10

// todo: devise better way for WGM here since we have to write 2 regs
#define TIMER_1_WGM_BASE         WGM10
#define TIMER_1_WGM_MODE_NORMAL  0b00 // todo: possibly add more but probably don't need now
#define TIMER_1_WGM_MODE_CTC     0b100

#define SET_TIMER_0_MODE_NORMAL SET_BITS(TCCR0A, TIMER_0_WGM_MODE_NORMAL, TIMER_0_WGM_BASE)
#define SET_TIMER_0_MODE_CTC    SET_BITS(TCCR0A, TIMER_0_WGM_MODE_CTC, TIMER_0_WGM_BASE)
#define TURN_TIMER_0_ON         SET_BITS(TCCR0B, TIMER_PRESCALE_1024, CS00)
#define TURN_TIMER_0_OFF        SET_BITS(TCCR0B, TIMER_OFF, CS00) // todo: how do I make this generic for the prescalar and output compare reg??
// todo: timer 1 stuff

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

#define POWER_STATUS_MASK      (1 << POWER_PIN_REG)
#define FAULT_STATUS_MASK      (1 << FAULT_PIN_REG)
#define DEV_MODE_STATUS_MASK   (1 << DEV_MODE_PIN_REG)
#define DEVICE_ACK_STATUS_MASK (1 << DEVICE_ACK_PIN_REG)
#define BUTTON_STATUS_MASK     (1 << BUTTON_PIN_REG)
#define RTC_ALARM_STATUS_MASK  (1 << RTC_ALARM_PIN_REG)

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

#define GPIOR2_POWER_FLAG_MASK    (1 << GPIOR2_POWER_FLAG_REG)
#define GPIOR2_FAULT_FLAG_MASK    (1 << GPIOR2_FAULT_FLAG_REG)
#define GPIOR2_DEV_MODE_FLAG_MASK (1 << GPIOR2_DEV_MODE_FLAG_REG)

#define SET_POWER_FLAG     SET_BIT(GPIOR2, GPIOR2_POWER_FLAG_REG)
#define CLR_POWER_FLAG     CLR_BIT(GPIOR2, GPIOR2_POWER_FLAG_REG)
#define SET_FAULT_FLAG     SET_BIT(GPIOR2, GPIOR2_FAULT_FLAG_REG)
#define CLR_FAULT_FLAG     CLR_BIT(GPIOR2, GPIOR2_FAULT_FLAG_REG)
#define SET_DEV_MODE_FLAG  SET_BIT(GPIOR2, GPIOR2_DEV_MODE_FLAG_REG)
#define CLR_DEV_MODE_FLAG  CLR_BIT(GPIOR2, GPIOR2_DEV_MODE_FLAG_REG)



// functions for checking pin states
// todo: where to put these??
// todo: better way to avoid if{} statement??
static inline int powerIsOn(void)
{
  return (POWER_PIN & POWER_STATUS_MASK);
}

static inline int powerFlagIsSet(void)
{
  if (GPIOR2 & GPIOR2_POWER_FLAG_MASK)
  {
    return 1;
  }
  else
  {
    return 0;
  }
}

static inline int faultIsOn(void)
{
  return (FAULT_PIN & FAULT_STATUS_MASK);
}

static inline int faultFlagIsSet(void)
{
  if (GPIOR2 & GPIOR2_FAULT_FLAG_MASK)
  {
    return 1;
  }
  else
  {
    return 0;
  }
}

static inline int devModeIsOn(void)
{
  return (DEV_MODE_PIN & DEV_MODE_STATUS_MASK);
}

static inline int devModeFlagIsSet(void)
{
  if (GPIOR2 & GPIOR2_DEV_MODE_FLAG_MASK)
  {
    return 1;
  }
  else
  {
    return 0;
  }
}

static inline int deviceAckIsOn(void)
{
  return (DEVICE_ACK_PIN & DEVICE_ACK_STATUS_MASK);
}

static inline int buttonIsOn(void) // look for low-going edge (active low)
{
  if (BUTTON_PIN & BUTTON_STATUS_MASK)
  {
    return 0;
  }
  else
  {
    return 1;
  }
}

static inline int rtcAlarmIsOn(void) // look for low-going edge (active low)
{
  if (RTC_ALARM_PIN & RTC_ALARM_STATUS_MASK)
  {
    return 0;
  }
  else
  {
    return 1;
  }
}

static inline int timer0IsOn(void)
{
  if (TCCR0B & TIMER_ON_MASK)
  {
    return 1;
  }
  else
  {
    return 0;
  }
}


static inline int timer1IsOn(void)
{
  if (TCCR1B & TIMER_ON_MASK)
  {
    return 1;
  }
  else
  {
    return 0;
  }
}

// function prototypes or whatever it's called here
static inline void initPortA(void);
static inline void initPortB(void);
static inline void initInterrupts(void);
static inline void initMCU(void);
static inline void startDebounceTimer_12ms(void);

