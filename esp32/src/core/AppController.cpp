#include <Arduino.h>

#include "AppController.h"
#include "../audio/AudioManager.h"
#include "Config.h"
#include "SystemUtils.h"
#include "../network/WifiManager.h"

void setupApp(AppState& state) {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting ESP32 Audio Assistant...");

  pinMode(Config::kLedRecPin, OUTPUT);
  pinMode(Config::kLedSysPin, OUTPUT);
  pinMode(Config::kButtonPin, INPUT_PULLUP);
  pinMode(Config::kDac1Pin, OUTPUT);
  pinMode(Config::kDac2Pin, OUTPUT);

  digitalWrite(Config::kLedRecPin, LOW);
  digitalWrite(Config::kLedSysPin, LOW);

  delay(100);

  setupWiFi();
  connectWiFi();
  setupAudioHardware();

  Serial.println("\n========================================");
  Serial.println("System Ready!");
  Serial.printf("Memory: Free %d bytes, Heap %d bytes\n", ESP.getFreeHeap(), ESP.getHeapSize());
  Serial.println("Press button to record (2 seconds)");
  Serial.println("Hold button >2s for system reset");
  Serial.println("========================================\n");

  blinkLED(Config::kLedSysPin, 3);
  state.lastWiFiCheck = millis();
}

void loopApp(AppState& state) {
  maintainWiFiConnection(state);

  static unsigned long lastDebounceTime = 0;
  static int lastButtonState = HIGH;
  static int buttonState = HIGH;

  const int currentButtonRead = digitalRead(Config::kButtonPin);
  if (currentButtonRead != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > Config::kDebounceDelayMs) {
    if (currentButtonRead != buttonState) {
      buttonState = currentButtonRead;

      if (buttonState == LOW && !state.buttonPressed) {
        state.buttonPressed = true;
        state.pressStartTime = millis();
        Serial.println("Button pressed...");
      } else if (buttonState == HIGH && state.buttonPressed) {
        state.buttonPressed = false;
        const unsigned long pressDuration = millis() - state.pressStartTime;

        if (pressDuration > Config::kLongPressMs) {
          Serial.println("Long press detected - Resetting system...");
          resetSystem();
        } else if (!state.isRecording) {
          startRecording(state);
        } else {
          Serial.println("Recording in progress, please wait...");
        }
      }
    }
  }

  lastButtonState = currentButtonRead;

  if (state.buttonPressed && !state.isRecording) {
    const unsigned long pressDuration = millis() - state.pressStartTime;
    if (pressDuration > Config::kLongPressMs) {
      Serial.println("Long press detected - Release to reset...");
      blinkLED(Config::kLedSysPin, 1);
    }
  }

  delay(50);
}
