/**
 * \file
 *
 * \brief User board configuration template
 *
 */
/*
 * Support and FAQ: visit <a href="http://www.atmel.com/design-support/">Atmel Support</a>
 */

#ifndef CONF_BOARD_H
#define CONF_BOARD_H

#define CONSOLE_UART                (Usart *)UART0

// clock resonators
#define BOARD_FREQ_SLCK_XTAL      (32768U)
#define BOARD_FREQ_SLCK_BYPASS    (32768U)
#define BOARD_FREQ_MAINCK_XTAL    (12000000U)
#define BOARD_FREQ_MAINCK_BYPASS  (12000000U)
#define BOARD_MCK                 CHIP_FREQ_CPU_MAX
#define BOARD_OSC_STARTUP_US      15625

/*
// --test bullshit--
// BROCCOLI will die if this is the only thing we define, guy.
// output pin for LED
#define LED0         IOPORT_CREATE_PIN(PIOB, 14)
// input pin for switch
#define SW0          IOPORT_CREATE_PIN(PIOA, 30)
*/


#endif // CONF_BOARD_H
