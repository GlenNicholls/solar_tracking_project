#include <stdbool.h>


// todo: what does the F_CPU do hardware wise? Does changing this value use hardware freq. synth. or
//       is it simply a software definition for something that is embedded??
#define F_CPU 8000000 // todo: lower clock... dummy
//#define F_CPU 1000000UL

// used for a very short delay
#define _NOP() do { __asm__ __volatile__ ("nop"); } while (0)

// todo: where is the header for these things??
// define macros
#define SET_BIT(PORT, BIT)        PORT |=  (1 << BIT)
#define CLR_BIT(PORT, BIT)        PORT &= ~(1 << BIT)
#define SET_OUTPUT(DDRX, BIT)     DDRX |=  (1 << BIT)
#define SET_INPUT(DDRX, BIT)      DDRX &= ~(1 << BIT)
#define SET_PULLUP_ON(PORT, BIT)  PORT |=  (1 << BIT)
#define SET_PULLUP_OFF(PORT, BIT) PORT &= ~(1 << BIT)

#define SET_BITS(REG, VAL, BASE) REG |= (VAL << BASE)

// INT values
#define LOGIC_CHANGE 0b01

// define pins for readability
// todo: make names more clear, e.g. POWER_PIN, PORT_PIN_POWER... These might be confusing
#define POWER_PIN      PA0
#define FAULT_PIN      PA1
#define DEV_MODE_PIN   PA3
#define DEVICE_ACK_PIN PA7
#define BUTTON_PIN     PB1
#define RTC_ALARM_PIN  PB2

#define POWER_PORT      PORTA
#define FAULT_PORT      PORTA
#define DEV_MODE_PORT   PORTA
#define DEVICE_ACK_PORT PORTA
#define BUTTON_PORT     PORTB
#define RTC_ALARM_PORT  PORTB

#define PIN_PORT_POWER      PINA
#define PIN_PORT_FAULT      PINA
#define PIN_PORT_DEV_MODE   PINA
#define PIN_PORT_DEVICE_ACK PINA
#define PIN_PORT_BUTTON     PINB
#define PIN_PORT_RTC_ALARM  PINB

#define TURN_POWER_ON     SET_BIT(POWER_PORT, POWER_PIN)
#define TURN_POWER_OFF    CLR_BIT(POWER_PORT, POWER_PIN)
#define TURN_FAULT_ON     SET_BIT(FAULT_PORT, FAULT_PIN)
#define TURN_FAULT_OFF    CLR_BIT(FAULT_PORT, FAULT_PIN)
#define TURN_DEV_MODE_ON  SET_BIT(DEV_MODE_PORT, DEV_MODE_PIN)
#define TURN_DEV_MODE_OFF CLR_BIT(DEV_MODE_PORT, DEV_MODE_PIN)

// Timer defines
// todo: setFlag() for checking timer in other ISR

// functions for checking pin states
// todo: should getSomething convention be used instead??
static inline bool isPowerOn(void)
{
  return (PIN_PORT_POWER & (1 << POWER_PIN)) > 0;
}

static inline bool isFaultOn(void)
{
  return (PIN_PORT_FAULT & (1 << FAULT_PIN)) > 0;
}

static inline bool isDevModeOn(void)
{
  return (PIN_PORT_DEV_MODE & (1 << DEV_MODE_PIN)) > 0;
}

static inline bool isDeviceAckOn(void)
{
  return (PIN_PORT_DEVICE_ACK & (1 << DEVICE_ACK_PIN)) > 0;
}

static inline bool isButtonOn(void) // look for low-going edge (active low)
{
  return (PIN_PORT_BUTTON & (1 << BUTTON_PIN)) == 0;
}

static inline bool isRTCAlarmOn(void) // look for low-going edge (active low)
{
  return (PIN_PORT_RTC_ALARM & (1 << RTC_ALARM_PIN)) == 0;
}
