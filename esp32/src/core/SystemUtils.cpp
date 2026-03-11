#include <Arduino.h>

#include "Config.h"
#include "SystemUtils.h"

void blinkLED(int pin, int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(100);
    digitalWrite(pin, LOW);
    delay(100);
  }
}

void resetSystem() {
  Serial.println("Resetting system...");
  blinkLED(Config::kLedSysPin, 5);
  delay(1000);
  ESP.restart();
}
