#include <attiny84.h>


/*****************************
 * Define HW Pins
 *****************************/
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



/*****************************
 * Pin Assertions
 *****************************/
// todo: possibly change to toggling?
#define TURN_POWER_ON      SET_BIT(POWER_PORT,    POWER_PIN_REG)
#define TURN_POWER_OFF     CLR_BIT(POWER_PORT,    POWER_PIN_REG)
#define TURN_FAULT_ON      SET_BIT(FAULT_PORT,    FAULT_PIN_REG)
#define TURN_FAULT_OFF     CLR_BIT(FAULT_PORT,    FAULT_PIN_REG)
#define TURN_DEV_MODE_ON   SET_BIT(DEV_MODE_PORT, DEV_MODE_PIN_REG)
#define TURN_DEV_MODE_OFF  CLR_BIT(DEV_MODE_PORT, DEV_MODE_PIN_REG)



/*****************************
 * GPIO User Registers
 *****************************/
#define GPIOR2_POWER_FLAG_REG        7
#define GPIOR2_FAULT_FLAG_REG        6
#define GPIOR2_DEV_MODE_FLAG_REG     5
#define GPIOR2_ALARM_CHECK_FLAG_REG  4
#define GPIOR2_SHUTDOWN_DLY_FLAG_REG 3

#define SET_POWER_FLAG  SET_BIT(GPIOR2, GPIOR2_POWER_FLAG_REG)
#define TGL_POWER_FLAG  TGL_BIT(GPIOR2, GPIOR2_POWER_FLAG_REG)
#define CLR_POWER_FLAG  CLR_BIT(GPIOR2, GPIOR2_POWER_FLAG_REG)

#define SET_FAULT_FLAG  SET_BIT(GPIOR2, GPIOR2_FAULT_FLAG_REG)
#define TGL_FAULT_FLAG  TGL_BIT(GPIOR2, GPIOR2_FAULT_FLAG_REG)
#define CLR_FAULT_FLAG  CLR_BIT(GPIOR2, GPIOR2_FAULT_FLAG_REG)

#define SET_DEV_MODE_FLAG  SET_BIT(GPIOR2, GPIOR2_DEV_MODE_FLAG_REG)
#define TGL_DEV_MODE_FLAG  TGL_BIT(GPIOR2, GPIOR2_DEV_MODE_FLAG_REG)
#define CLR_DEV_MODE_FLAG  CLR_BIT(GPIOR2, GPIOR2_DEV_MODE_FLAG_REG)

#define SET_ALARM_CHECK_FLAG  SET_BIT(GPIOR2, GPIOR2_ALARM_CHECK_FLAG_REG)
#define TGL_ALARM_CHECK_FLAG  TGL_BIT(GPIOR2, GPIOR2_ALARM_CHECK_FLAG_REG)
#define CLR_ALARM_CHECK_FLAG  CLR_BIT(GPIOR2, GPIOR2_ALARM_CHECK_FLAG_REG)

#define SET_SHUTDOWN_DLY_FLAG  SET_BIT(GPIOR2, GPIOR2_SHUTDOWN_DLY_FLAG_REG)
#define TGL_SHUTDOWN_DLY_FLAG  TGL_BIT(GPIOR2, GPIOR2_SHUTDOWN_DLY_FLAG_REG)
#define CLR_SHUTDOWN_DLY_FLAG  CLR_BIT(GPIOR2, GPIOR2_SHUTDOWN_DLY_FLAG_REG)



/*****************************
 * HW Port Configuration
 *****************************/
// todo: set full register if need memory
// todo: put all hardware specific in attiny84a.h
// todo: use pullup and figure out direction for unused pins (including ICSP)
//       ref page 56
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
  SET_PULLUP_ON(PORTA, DEV_MODE_PIN_REG); // Make sure to turn off during initMCU
  SET_PULLUP_ON(PORTA, PA2);              // not connected
  SET_PULLUP_ON(PORTA, FAULT_PIN_REG);    // Make sure to turn off during initMCU
  SET_PULLUP_ON(PORTA, POWER_PIN_REG);

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



/*****************************
 * Pin State Helpers
 *****************************/
// todo: where to put these??
static inline int powerIsOn(void)
{
  return bit_is_set(POWER_PIN, POWER_PIN_REG);
}

static inline int faultIsOn(void)
{
  return bit_is_set(FAULT_PIN, FAULT_PIN_REG);
}

static inline int devModeIsOn(void)
{
  return bit_is_set(DEV_MODE_PIN, DEV_MODE_PIN_REG);
}

static inline int deviceAckIsOn(void)
{
  return bit_is_set(DEVICE_ACK_PIN, DEVICE_ACK_PIN_REG);
}

static inline int buttonIsOn(void) // look for low-going edge (active low)
{
  return bit_is_clear(BUTTON_PIN, BUTTON_PIN_REG);
}

static inline int rtcAlarmIsOn(void) // look for low-going edge (active low)
{
  return bit_is_clear(RTC_ALARM_PIN, RTC_ALARM_PIN_REG);
}



/*****************************
 * GPIO Reg Flag State Helpers
 *****************************/
static inline int powerFlagIsSet(void)
{
  return bit_is_set(GPIOR2, GPIOR2_POWER_FLAG_REG);
}

static inline int faultFlagIsSet(void)
{
  return bit_is_set(GPIOR2, GPIOR2_FAULT_FLAG_REG);
}

static inline int devModeFlagIsSet(void)
{
  return bit_is_set(GPIOR2, GPIOR2_DEV_MODE_FLAG_REG);
}

static inline int checkAlarmFlagIsSet(void)
{
  return bit_is_set(GPIOR2, GPIOR2_ALARM_CHECK_FLAG_REG);
}

static inline int shutdownDelayFlagIsSet(void)
{
  return bit_is_set(GPIOR2, GPIOR2_SHUTDOWN_DLY_FLAG_REG);
}



/*****************************
 * Timer Helpers
 *****************************/
static inline int timer0IsOn(void)
{
  return (TCCR0B & TIMER_ON_MASK);
}

static inline int timer1IsOn(void)
{
  return (TCCR1B & TIMER_ON_MASK);
}
