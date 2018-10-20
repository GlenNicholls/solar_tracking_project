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

// INT values
#define LOGIC_CHANGE 0b01

// define pins for readability
#define POWER_PIN_REG      PA0
#define FAULT_PIN_REG      PA1
#define DEV_MODE_PIN_REG   PA3
#define DEVICE_ACK_PIN_REG PA7
#define BUTTON_PIN_REG     PB1
#define RTC_ALARM_PIN_REG  PB2

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

// todo: abstract this to general reg and analyze in main
#define TURN_POWER_ON     SET_BIT(POWER_PORT,    POWER_PIN_REG)
#define TURN_POWER_OFF    CLR_BIT(POWER_PORT,    POWER_PIN_REG)
#define TURN_FAULT_ON     SET_BIT(FAULT_PORT,    FAULT_PIN_REG)
#define TURN_FAULT_OFF    CLR_BIT(FAULT_PORT,    FAULT_PIN_REG)
#define TURN_DEV_MODE_ON  SET_BIT(DEV_MODE_PORT, DEV_MODE_PIN_REG)
#define TURN_DEV_MODE_OFF CLR_BIT(DEV_MODE_PORT, DEV_MODE_PIN_REG)


// Timer defines
// todo: setFlag() for checking timer in other ISR

// functions for checking pin states
// todo: where to put these??
static inline int powerIsOn(void)
{
  return (POWER_PIN & POWER_STATUS_MASK);
}

static inline int faultIsOn(void)
{
  return (FAULT_PIN & FAULT_STATUS_MASK);
}

static inline int devModeIsOn(void)
{
  return (DEV_MODE_PIN & DEV_MODE_STATUS_MASK);
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

// function prototypes or whatever it's called here
static inline void initPortA(void);
static inline void initPortB(void);
static inline void initInterrupts(void);
static inline void initMCU(void);

