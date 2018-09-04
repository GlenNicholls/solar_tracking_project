#include "ADA254.h"

ADA254::ADA254(uint8_t _chipSelect) {
    chipSelect = _chipSelect;
}

void ADA254::Init() {
  Serial.println("\n-I- Initializing SD card...");
  bool SdBeginValid = SD.begin(chipSelect);

  // see if the card is present and can be initialized:
  if (!SdBeginValid) {
    Serial.println("-E- initialization failed. Things to check:");
    Serial.println("  * is a card inserted?");
    Serial.println("  * is your wiring correct?");
    Serial.println("  * did you change the chipSelect pin to match your shield or module?");

  }
  else {
    Serial.println("-I- card initialized.");
  }

}

void ADA254::CardInfo() {
  Serial.print("\n-I- Generating SD card info...");
  // we'll use the initialization code from the utility libraries
  // since we're just testing if the card is working!
  if (!card.init(SPI_HALF_SPEED, chipSelect)) {
    Serial.println("-E- initialization failed. Things to check:");
    Serial.println("* is a card inserted?");
    Serial.println("* is your wiring correct?");
    Serial.println("* did you change the chipSelect pin to match your shield or module?");
    return;
  } else {
    Serial.println("-I- Wiring is correct and a card is present.");
  }

  // print the type of card
  Serial.print("\nCard type: ");
  switch (card.type()) {
    case SD_CARD_TYPE_SD1:
      Serial.println("-I- SD1");
      break;
    case SD_CARD_TYPE_SD2:
      Serial.println("-I- SD2");
      break;
    case SD_CARD_TYPE_SDHC:
      Serial.println("-I- SDHC");
      break;
    default:
      Serial.println("-E- Unknown");
  }

  // Now we will try to open the 'volume'/'partition' - it should be FAT16 or FAT32
  if (!volume.init(card)) {
    Serial.println("-E- Could not find FAT16/FAT32 partition.\nMake sure you've formatted the card");
    return;
  }


  // print the type and size of the first FAT-type volume
  uint32_t volumesize;
  Serial.print("\n-I- Volume type is FAT");
  Serial.println(volume.fatType(), DEC);
  Serial.println();

  volumesize = volume.blocksPerCluster();    // clusters are collections of blocks
  volumesize *= volume.clusterCount();       // we'll have a lot of clusters
  volumesize *= 512;                            // SD card blocks are always 512 bytes
  Serial.print("-I- Volume size (bytes): ");
  Serial.println(volumesize);
  Serial.print("-I- Volume size (Kbytes): ");
  volumesize /= 1024;
  Serial.println(volumesize);
  Serial.print("-I- Volume size (Mbytes): ");
  volumesize /= 1024;
  Serial.println(volumesize);


  Serial.println("\n-I- Files found on the card (name, date and size in bytes): ");
  root.openRoot(volume);

  // list all files in the card with date and size
  root.ls(LS_R | LS_DATE | LS_SIZE);
}

void ADA254::WriteFileLine(String filename, String strToWr) {
  File dataFile;

  // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  dataFile = SD.open(filename, FILE_WRITE);

  // if the file is available, write to it
  if (dataFile) {
    dataFile.println(strToWr);
    //delay(100);
    // print to the serial port too:
    Serial.println(String("-I- Writing to file: ") + strToWr);
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("-E- Cannot open file!");
  }
  dataFile.close();
}

String ADA254::ReadFileLine(String filename) {
  // init string to read from file
  String strFromFile = "";

  // start communication with the SD card
  if (!SD.exists(filename)) {
    Serial.println("-E- " + filename + " DOES NOT exist!");
  }

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
    Serial.println("-E- cannot open file!");
  }

  return strFromFile;
}


