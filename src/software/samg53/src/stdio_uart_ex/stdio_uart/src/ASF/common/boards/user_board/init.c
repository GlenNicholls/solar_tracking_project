/**
 * \file
 *
 * \brief User board initialization template
 *
 */
/*
 * Support and FAQ: visit <a href="http://www.atmel.com/design-support/">Atmel Support</a>
 */

#include <asf.h>
#include <board.h>
#include <conf_board.h>

void board_init(void)
{
	/* This function is meant to contain board-specific initialization code
	 * for, e.g., the I/O pins. The initialization can rely on application-
	 * specific board configuration, found in conf_board.h.
	 */
	
	// watchdog timer
	WDT->WDT_MR = WDT_MR_WDDIS;                    // disable watchdog
	
	// io
	ioport_init();                                 // call before using IOPORT service
	
	// configure UART pins
	// pa9/pa10 set use internal periph a which is uart0 by calling ioport_set_port_mode().
	// these two uart pins then disabled as io by calling ioport_disable_port() to dedicate
	// to uart.
	ioport_set_port_mode(IOPORT_PIOA, PIO_PA9A_URXD0 | PIO_PA10A_UTXD0, IOPORT_MODE_MUX_A);
	ioport_disable_port(IOPORT_PIOA, PIO_PA9A_URXD0 | PIO_PA10A_UTXD0);
	
	/* example for io */
	//ioport_set_pin_dir(LED0, IOPORT_DIR_OUTPUT);   // LED pin set as output
	//ioport_set_pin_dir(SW0, IOPORT_DIR_INPUT);     // switch pin set as input
	
}
