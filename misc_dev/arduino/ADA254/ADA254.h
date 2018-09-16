#ifndef ADA254_h
#define ADA254_h

#include <Arduino.h>
#include <SPI.h>
#include <SD.h>

class ADA254 {
public:
    ADA254(uint8_t _chipSelect);
    void CardInfo();
    void Init();
    void WriteFileLine(String filename, String strToWr);
    String ReadFileLine(String filename);
private:
    // set up variables using the SD utility library functions:
    Sd2Card card;
    SdVolume volume;
    SdFile root;
    uint8_t chipSelect;
};
#endif // ADA254

