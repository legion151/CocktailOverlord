
#include "Adafruit_NeoPixel.h"


#define PIN            14
#define NUMPIXELS      76
#define SERIAL_RX_BUFFER_SIZE 1024



Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

unsigned long lastInput = 0;
unsigned long curMillis = 0;
byte buf[4];
String inputString = "";
int j = 0;
int commandCount = 0;
int bytes = 0;
int frameCount = 0;
uint32_t  color = 0;
int ledCount = 0;
int hadInput = 0;

void setup() {

  inputString.reserve(512);

  // put your setup code here, to run once:
  pixels.begin();
  Serial.begin(115200);     // opens serial port, sets data rate to 9600 bps
  //lastInput = millis();

  curMillis = lastInput;
  pixels.show();



}


void loop() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    if (bytes == 0 && (inChar != 0xff))
    {
      pixels.setPixelColor(0, pixels.Color(100, 0, 0));
      pixels.show();
      continue;
    }



    inputString += inChar;
    bytes ++;
    if (bytes == 5)
    {
      commandCount++;
      bytes = 0;

      //lastInput = millis();

      //  Serial.print(1);
    }

    if (commandCount > 14)
    {
      hadInput = 1;
      break;
    }



  }


 // curMillis = millis();



  if (hadInput == 0)
  {
    pixels.setPixelColor(0, pixels.Color(0, 0, 0));

    j++;
    if (j == 265)
      j = 0;
    for (int i = 1; i < NUMPIXELS; i++)
    {
      pixels.setPixelColor(i, Wheel(((i * 256 / pixels.numPixels()) + j) & 255));
    }
  }
  else
  {
    while (commandCount > 0)
    {
      buf[0] = inputString.charAt(1);
      buf[1] = inputString.charAt(2);
      buf[2] = inputString.charAt(3);
      buf[3] = inputString.charAt(4);
      inputString.remove(0, 5);

      pixels.setPixelColor(0, pixels.Color(0, 0, 0));

      commandCount--;

      if (buf[0] == 0xff  && buf[1] == 0xff && buf[2] == 0xff && buf[3] == 0xff )
      {
        // goto hell
        for (int i = 0; i < 10; i++)
          Serial.write("HELLFIRE");
        Serial.flush();

      }
      else
      {
        color  = pixels.Color(buf[1], buf[2], buf[3]);
        for (ledCount = 0; ledCount < 5; ledCount++)
        {

          pixels.setPixelColor((buf[0] * 5) +ledCount + 1, color);
        }

      }
    }
  }
  pixels.show();

}


uint32_t Wheel(byte WheelPos) {
  if (WheelPos < 85) {
    return pixels.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
  } else if (WheelPos < 170) {
    WheelPos -= 85;
    return pixels.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  } else {
    WheelPos -= 170;
    return pixels.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  }
}




