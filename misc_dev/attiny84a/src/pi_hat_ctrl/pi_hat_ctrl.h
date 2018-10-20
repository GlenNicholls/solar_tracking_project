#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include <stdbool.h>


// todo: what does the F_CPU do hardware wise? Does changing this value use hardware freq. synth. or
//       is it simply a software definition for something that is embedded??
#define F_CPU 8000000 // todo: lower clock... dummy
//#define F_CPU 1000000UL

// used for a very short delay
#define _NOP() do { __asm__ __volatile__ ("nop"); } while (0)

// todo: where is the header for these things??
// define macros
#define SET_BIT(PORT, BIT) ( PORT |=  (1 << BIT) )
#define CLR_BIT(PORT, BIT) ( PORT &= ~(1 << BIT) )

#define SET_OUTPUT(DDRX, BIT) ( DDRX |=  (1 << BIT) )
#define SET_INPUT(DDRX, BIT)  ( DDRX &= ~(1 << BIT) )

#define SET_PULLUP_ON(PORT, BIT)  ( PORT |=  (1 << BIT) )
#define SET_PULLUP_OFF(PORT, BIT) ( PORT &= ~(1 << BIT) )

#define SET_BITS(REG, VAL, BASE) ( REG |= (VAL << BASE) )
#define CLR_BITS(REG, VAL, BASE) ( REG &= ~(VAL << BASE))

#define GET_PIN_STATUS(PIN, MASK) (PIN & MASK)

// INT values
#define LOGIC_CHANGE 0b01

// define pins for readability
// todo: make names more clear, e.g. POWER_PIN, PORT_PIN_POWER... These might be confusing
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

// todo: is this what you meant by moving function to define or #define (<whatever> & SOMETHING_STATUS_MASK)
#define IS_POWER_ON      GET_PIN_STATUS(POWER_PIN,      POWER_STATUS_MASK)
#define IS_FAULT_ON      GET_PIN_STATUS(FAULT_PIN,      FAULT_STATUS_MASK)
#define IS_DEV_MODE_ON   GET_PIN_STATUS(DEV_MODE_PIN,   DEV_MODE_STATUS_MASK)
#define IS_DEVICE_ACK_ON GET_PIN_STATUS(DEVICE_ACK_PIN, DEVICE_ACK_STATUS_MASK)
#define IS_BUTTON_OFF    GET_PIN_STATUS(BUTTON_PIN,     BUTTON_STATUS_MASK)    // inverted logic, will ~
#define IS_RTC_ALARM_OFF GET_PIN_STATUS(RTC_ALARM_PIN,  RTC_ALARM_STATUS_MASK) // inverted logic, will ~

// todo: not sure if this inverting logic is valid, I think so since it's already masked so should be 0xff when true
#define IS_BUTTON_ON    (~IS_BUTTON_OFF)
#define IS_RTC_ALARM_ON (~IS_RTC_ALARM_OFF)

// Timer defines
// todo: setFlag() for checking timer in other ISR

// // functions for checking pin states
// // todo: should getSomething convention be used instead??
// static inline bool isPowerOn(void)
// {
//   return (POWER_PIN & (1 << POWER_PIN_REG)) > 0;
// }
//
// static inline bool isFaultOn(void)
// {
//   return (FAULT_PIN & (1 << FAULT_PIN_REG)) > 0;
// }
//
// static inline bool isDevModeOn(void)
// {
//   return (DEV_MODE_PIN & (1 << DEV_MODE_PIN_REG)) > 0;
// }
//
// static inline bool isDeviceAckOn(void)
// {
//   return (DEVICE_ACK_PIN & (1 << DEVICE_ACK_PIN_REG)) > 0;
// }
//
// static inline bool isButtonOn(void) // look for low-going edge (active low)
// {
//   return (BUTTON_PIN & (1 << BUTTON_PIN_REG)) == 0;
// }
//
// static inline bool isRTCAlarmOn(void) // look for low-going edge (active low)
// {
//   return (RTC_ALARM_PIN & (1 << RTC_ALARM_PIN_REG)) == 0;
// }

// function prototypes
// todo: hmmm
static inline void initPortA(void);
static inline void initPortB(void);
static inline void initInterrupts(void);
static inline void initMCU(void);

