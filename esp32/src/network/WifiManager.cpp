#include <Arduino.h>
#include <WiFi.h>

#include "../core/Config.h"
#include "../core/SystemUtils.h"
#include "WifiManager.h"

namespace {

void handleWiFiEvent(WiFiEvent_t event, arduino_event_info_t info) {
  (void)info;

  switch (event) {
    case ARDUINO_EVENT_WIFI_STA_CONNECTED:
      Serial.println("WiFi connected to AP");
      break;
    case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
      Serial.println("WiFi disconnected from AP");
      digitalWrite(Config::kLedSysPin, LOW);
      break;
    case ARDUINO_EVENT_WIFI_STA_GOT_IP:
      Serial.println("Got IP address");
      Serial.print("IP: ");
      Serial.println(WiFi.localIP());
      digitalWrite(Config::kLedSysPin, HIGH);
      break;
    default:
      break;
  }
}

}  // namespace

void setupWiFi() {
  WiFi.persistent(false);
  WiFi.onEvent(handleWiFiEvent);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.setSleep(false);
}

void connectWiFi() {
  Serial.println("Connecting to WiFi...");

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Already connected to WiFi");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    digitalWrite(Config::kLedSysPin, HIGH);
    return;
  }

  WiFi.mode(WIFI_OFF);
  delay(500);
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  delay(200);
  WiFi.setAutoReconnect(true);
  WiFi.setSleep(false);
  WiFi.begin(Config::kSsid, Config::kPassword);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    yield();
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    digitalWrite(Config::kLedSysPin, HIGH);
  } else {
    Serial.println("\nWiFi connection failed");
    blinkLED(Config::kLedSysPin, 5);
  }
}

void maintainWiFiConnection(AppState& state) {
  const unsigned long currentTime = millis();
  if (currentTime - state.lastWiFiCheck <= Config::kWifiCheckIntervalMs) {
    return;
  }

  state.lastWiFiCheck = currentTime;
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  Serial.println("WiFi disconnected, reconnecting...");
  digitalWrite(Config::kLedSysPin, LOW);
  WiFi.reconnect();

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 10) {
    delay(500);
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    digitalWrite(Config::kLedSysPin, HIGH);
    Serial.println("WiFi reconnected");
  } else {
    connectWiFi();
  }
}
