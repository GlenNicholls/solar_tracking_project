# ======================================================================
#  Makefile for AVRDude
# ======================================================================
MCU    = attiny84

TARGET = pi_hat_ctrl
SRC    = main.c pi_hat_ctrl.h $(MCU).h 


# ======================================================================
# You shouldn't have to edit below this line
# ======================================================================
AVRDUDE = avrdude
CC      = avr-gcc
OBJCOPY = avr-objcopy

CFLAGS = -Wall -Os -std=gnu99 -mmcu=$(MCU) -I.

AVRDUDE_CONF        = ../../../avrdude_gpio.conf
AVRDUDE_PROGRAMMER  = pi_1
AVRDUDE_WRITE_FLASH = -U flash:w:$(TARGET).hex
AVRDUDE_FLAGS       = -p $(MCU) -c $(AVRDUDE_PROGRAMMER) -C $(AVRDUDE_CONF) -v

all:
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)
	$(OBJCOPY) -O ihex -R .eeprom $(TARGET) $(TARGET).hex
	avr-size -C --mcu=$(MCU) $(TARGET)

clean:
	rm -f $(TARGET) $(TARGET).hex

install: all
	sudo $(AVRDUDE) $(AVRDUDE_FLAGS) $(AVRDUDE_WRITE_FLASH)

fuse:
	sudo $(AVRDUDE) $(AVRDUDE_FLAGS) -U lfuse:w:0xE7:m -U hfuse:w:0xD9:m -U efuse:w:0x07:m

.PHONY: all clean install fuse
