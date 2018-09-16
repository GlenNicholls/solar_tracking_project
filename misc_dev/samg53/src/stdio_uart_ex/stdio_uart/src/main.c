/**
 * \file
 *
 * \brief Empty user application template
 *
 */

/**
 * \mainpage User Application template doxygen documentation
 *
 * \par Empty user application template
 *
 * Bare minimum empty user application template
 *
 * \par Content
 *
 * -# Include the ASF header files (through asf.h)
 * -# "Insert system clock initialization code here" comment
 * -# Minimal main function that starts with a call to board_init()
 * -# "Insert application code here" comment
 *
 */

/*
 * Include header files for all drivers that have been imported from
 * Atmel Software Framework (ASF).
 */
/*
 * Support and FAQ: visit <a href="http://www.atmel.com/design-support/">Atmel Support</a>
 */
#include <asf.h>

int main (void)
{
	const char str[] = "Type 'a' to continue...\r\n";
	uint8_t rx_char = 0;
	
	const usart_serial_options_t usart_serial_options = 
	{
		.baudrate     = CONF_UART_BAUDRATE,
		.charlength   = CONF_UART_CHAR_LENGTH,
		.paritytype   = CONF_UART_PARITY,
		.stopbits     = CONF_UART_STOP_BITS
	};

	/* board and sysClk init */	
	sysclk_init();
	board_init();

	/* uart init */
	// set up uart as standard io device
	stdio_serial_init(CONF_UART, &usart_serial_options);
	
	/* initial console message */
	//printf("\r\nHello, world!\r\n");
	
	// send a string using the write packet function
	usart_serial_write_packet(CONF_UART, (const uint8_t*)str, sizeof(str) - 1);
	do 
	{
		usart_serial_getchar(CONF_UART, &rx_char); // get single char
	} while (rx_char != 'a');
	// send a single character
	usart_serial_putchar(CONF_UART, 'A'); // echo cuz user is idiot
	
	//usart_serial_read_packet() function reads packet of certain length from uart
	
	/* main app */
	while (1) 
	{
		// nothing to see 
	} // end main app
} // end main
