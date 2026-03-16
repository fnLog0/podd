#include <Arduino.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFi.h>

#include "../app/RuntimeConfig.h"
#include "AudioUploader.h"

UploadResult uploadAudio(int16_t* samples, size_t size) {
  UploadResult result = { true, "" };

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, cannot upload");
    result.success = false;
    return result;
  }

  if (samples == nullptr || size == 0) {
    Serial.println("Invalid samples data");
    result.success = false;
    return result;
  }

  HTTPClient http;
  http.setTimeout(30000);

  if (!http.begin(Config::kServerUrl)) {
    Serial.println("Failed to begin HTTP connection");
    result.success = false;
    return result;
  }

  http.addHeader("Content-Type", "application/octet-stream");

  Serial.println("Sending data...");
  const int httpCode = http.POST(reinterpret_cast<uint8_t*>(samples), size);

  if (httpCode <= 0) {
    Serial.printf("Upload failed, error: %s\n", http.errorToString(httpCode).c_str());
    http.end();
    result.success = false;
    return result;
  }

  Serial.printf("Server response code: %d\n", httpCode);

  // HEAP-BASED RESPONSE READING: Use a heap buffer instead of stack to prevent stack overflow
  char* responseBuffer = static_cast<char*>(malloc(4096));
  if (responseBuffer == nullptr) {
    Serial.println("Failed to allocate response buffer");
    http.end();
    result.success = false;
    return result;
  }
  memset(responseBuffer, 0, 4096);
  
  if (httpCode == 200) {
    WiFiClient* stream = http.getStreamPtr();
    int totalRead = 0;
    const unsigned long startRead = millis();
    
    // Read up to 4095 bytes (leaving space for null terminator)
    while (http.connected() && totalRead < 4095 && (millis() - startRead < 5000)) {
      if (stream->available()) {
        int r = stream->read(reinterpret_cast<uint8_t*>(&responseBuffer[totalRead]), 4095 - totalRead);
        if (r > 0) totalRead += r;
      } else {
        delay(10);
      }
    }
    responseBuffer[totalRead] = '\0';
  }
  
  http.end();

  if (httpCode != 200) {
    Serial.printf("Server returned non-OK status: %d\n", httpCode);
    free(responseBuffer);
    result.success = false;
    return result;
  }

  const size_t respLen = strlen(responseBuffer);
  if (respLen < 10) {
    Serial.println("Server response too small or empty");
    free(responseBuffer);
    result.success = false;
    return result;
  }

  // Use the heap buffer for JSON parsing
  DynamicJsonDocument doc(4096);
  const DeserializationError jsonErr = deserializeJson(doc, responseBuffer);

  if (jsonErr) {
    Serial.printf("JSON error: %s (response length: %d)\n", jsonErr.c_str(), static_cast<int>(respLen));
    free(responseBuffer);
    result.success = false;
    return result;
  }

  if (!doc["success"]) {
    Serial.println("Server reported failure");
    free(responseBuffer);
    result.success = false;
    return result;
  }

  Serial.printf("Transcript: %s\n", doc["transcript"].as<const char*>());
  Serial.printf("AI Response: %s\n", doc["aiResponse"].as<const char*>());

  if (doc.containsKey("ttsAudioPath")) {
    const char* ttsPath = doc["ttsAudioPath"];
    if (ttsPath != nullptr) {
      String pathStr(ttsPath);
      const int lastSlash = pathStr.lastIndexOf('/');
      result.ttsFilename = lastSlash != -1 ? pathStr.substring(lastSlash + 1) : pathStr;
      result.ttsFilename = "output/" + result.ttsFilename;
      Serial.printf("TTS Audio: %s\n", result.ttsFilename.c_str());
    } else {
      Serial.println("TTS audio path is null");
    }
  } else {
    Serial.println("No TTS audio path in response");
  }

  free(responseBuffer);
  return result;
}
