# ======================================================================
#  Makefile for AVRDude
# ======================================================================
MCU          = attiny84
MCU_CPU_FREQ = 31250

TARGET       = pi_hat_ctrl
SRC          = main.c pi_hat_ctrl.h $(MCU).h 


# ======================================================================
# You shouldn't have to edit below this line
# ======================================================================
AVRDUDE = avrdude
CC      = avr-gcc
OBJCOPY = avr-objcopy

CFLAGS = -Wall -Os -std=gnu99 -mmcu=$(MCU) -I.

AVRDUDE_DBG         = -v
AVRDUDE_CONF        = ../../../avrdude_gpio.conf
AVRDUDE_PROGRAMMER  = pi_1
AVRDUDE_WRITE_FLASH = -U flash:w:$(TARGET).hex
AVRDUDE_ICSP_DLY_us = -i128
AVRDUDE_FLAGS       = -p $(MCU) -c $(AVRDUDE_PROGRAMMER) -C $(AVRDUDE_CONF) $(AVRDUDE_ICSP_DLY_us) $(AVRDUDE_DBG)

all:
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET) -DF_CPU=$(MCU_CPU_FREQ)
	$(OBJCOPY) -O ihex -R .eeprom $(TARGET) $(TARGET).hex
	avr-size -C --mcu=$(MCU) $(TARGET)

clean:
	rm -f $(TARGET) $(TARGET).hex

install: all
	sudo $(AVRDUDE) $(AVRDUDE_FLAGS) $(AVRDUDE_WRITE_FLASH)

fuse:
	sudo $(AVRDUDE) $(AVRDUDE_FLAGS) -U lfuse:w:0x62:m -U hfuse:w:0xDF:m -U efuse:w:0xFF:m

.PHONY: all clean install fuse
