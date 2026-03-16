#include <Arduino.h>

#include "ApplicationController.h"
#include "../audio/AudioService.h"
#include "RuntimeConfig.h"
#include "DeviceUtilities.h"
#include "../connectivity/WiFiService.h"

#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

void setupApp(AppState& state) {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Disable brownout detector
  
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
  const bool wifiOk = connectWiFi();
  if (!wifiOk) {
    Serial.println("WARNING: WiFi not connected at startup");
    // Recording will re-check WiFi before each attempt
  }

  const bool audioInitialized = setupAudioHardware();
  if (!audioInitialized) {
    Serial.println("WARNING: Audio hardware init failed");
    blinkLed(Config::kLedRecPin, 5);
    // Continue in degraded mode so the device remains reachable.
  }

  Serial.println("\n========================================");
  Serial.println("System Ready!");
  Serial.printf("Memory: Free %d bytes, Heap %d bytes\n", ESP.getFreeHeap(), ESP.getHeapSize());
  Serial.println("Press button to record (2 seconds)");
  Serial.println("Hold button >2s for system reset");
  Serial.println("========================================\n");

  blinkLed(Config::kLedSysPin, 3);
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
      blinkLed(Config::kLedSysPin, 1);
    }
  }

  delay(50);
}
