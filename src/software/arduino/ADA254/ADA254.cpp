#include "ADA254.h"

ADA254::ADA254(uint8_t _chipSelect) {
    chipSelect = _chipSelect;
}

void ADA254::Init() {
  Serial.print("\nInitializing SD card...");

  // we'll use the initialization code from the utility libraries
  // since we're just testing if the card is working!
  if (!card.init(SPI_HALF_SPEED, chipSelect)) {
    Serial.println("initialization failed. Things to check:");
    Serial.println("* is a card inserted?");
    Serial.println("* is your wiring correct?");
    Serial.println("* did you change the chipSelect pin to match your shield or module?");
    return;
  } else {
    Serial.println("Wiring is correct and a card is present.");
  }
  
  // print the type of card
  Serial.print("\nCard type: ");
  switch (card.type()) {
    case SD_CARD_TYPE_SD1:
      Serial.println("SD1");
      break;
    case SD_CARD_TYPE_SD2:
      Serial.println("SD2");
      break;
    case SD_CARD_TYPE_SDHC:
      Serial.println("SDHC");
      break;
    default:
      Serial.println("Unknown");
  }
  
  // Now we will try to open the 'volume'/'partition' - it should be FAT16 or FAT32
  if (!volume.init(card)) {
    Serial.println("Could not find FAT16/FAT32 partition.\nMake sure you've formatted the card");
    return;
  }
  
  
  // print the type and size of the first FAT-type volume
  uint32_t volumesize;
  Serial.print("\nVolume type is FAT");
  Serial.println(volume.fatType(), DEC);
  Serial.println();
  
  volumesize = volume.blocksPerCluster();    // clusters are collections of blocks
  volumesize *= volume.clusterCount();       // we'll have a lot of clusters
  volumesize *= 512;                            // SD card blocks are always 512 bytes
  Serial.print("Volume size (bytes): ");
  Serial.println(volumesize);
  Serial.print("Volume size (Kbytes): ");
  volumesize /= 1024;
  Serial.println(volumesize);
  Serial.print("Volume size (Mbytes): ");
  volumesize /= 1024;
  Serial.println(volumesize);
  
  
  Serial.println("\nFiles found on the card (name, date and size in bytes): ");
  root.openRoot(volume);
  
  // list all files in the card with date and size
  root.ls(LS_R | LS_DATE | LS_SIZE);
}

void ADA254::WriteFileLine(String filename, String strToWr) {
  // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  File dataFile;

  if (!SD.exists(filename)) {
    Serial.println(filename + " DOES NOT exist!");
    Serial.println("Creating " + filename);
    dataFile = SD.open(filename, FILE_WRITE);
    dataFile.close();
  }   

  if (SD.exists(filename)) {
    dataFile = SD.open(filename, FILE_WRITE);
  }
  else {
    Serial.println(filename + " still does not exist!!!");
  }

  
  // if the file is available, write to it:
  if (dataFile) {
    dataFile.println(strToWr);
    dataFile.close();
    // print to the serial port too:
    Serial.println(strToWr);
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("error opening file");
  }
}

String ADA254::ReadFileLine(String filename) {
  String strFromFile = "";
  // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  File dataFile = SD.open(filename);
  
  // if the file is available, write to it:
  if (dataFile) {
      // read from the file until there's nothing else in it:
      //while (dataFile.available()) {
        //strFromFile = dataFile.read();
        Serial.write(dataFile.read());
      //}
      // close the file:
      dataFile.close();
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("error opening file");
  }

  return strFromFile;
}


