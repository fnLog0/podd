#include <Arduino.h>
#include <HTTPClient.h>
#include <WiFi.h>

#include "../app/ApplicationState.h"
#include "../app/RuntimeConfig.h"
#include "../app/DeviceUtilities.h"
#include "AudioPlayer.h"

bool playTTSAudio(AppState& state, const String& filename) {
  if (state.isPlaying) {
    Serial.println("Audio already playing...");
    return false;
  }

  if (filename.isEmpty() || filename.length() > 256) {
    Serial.println("Invalid filename");
    blinkLed(Config::kLedRecPin, 3);
    return false;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, cannot play audio");
    blinkLed(Config::kLedRecPin, 3);
    return false;
  }

  Serial.printf("Memory before playback: %d bytes free\n", ESP.getFreeHeap());
  if (ESP.getFreeHeap() < 30000) {
    Serial.println("Not enough memory for audio playback");
    blinkLed(Config::kLedRecPin, 3);
    return false;
  }

  state.isPlaying = true;

  const String url = String(Config::kAudioBaseUrl) + filename;
  Serial.printf("Downloading TTS audio from: %s\n", url.c_str());

  HTTPClient http;
  int httpCode = -1;
  int retryCount = 0;
  const int maxRetries = 3;

  do {
    http.setTimeout(60000);

    if (!http.begin(url)) {
      Serial.println("Failed to begin HTTP connection");
      retryCount++;
      if (retryCount < maxRetries) {
        Serial.printf("Retrying... (%d/%d)\n", retryCount + 1, maxRetries);
        delay(1000);
        continue;
      }
      state.isPlaying = false;
      return false;
    }

    httpCode = http.GET();
    if (httpCode == HTTP_CODE_OK) {
      break;
    }

    Serial.printf("HTTP GET failed: %d\n", httpCode);
    http.end();
    retryCount++;

    if (retryCount < maxRetries) {
      Serial.printf("Retrying... (%d/%d)\n", retryCount + 1, maxRetries);
      delay(1000);
      if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Reconnecting WiFi...");
        WiFi.reconnect();
        delay(500);
      }
    } else {
      Serial.println("Max retries reached");
      state.isPlaying = false;
      return false;
    }
  } while (retryCount < maxRetries);

  if (httpCode == HTTP_CODE_OK) {
    const int len = http.getSize();
    Serial.printf("Audio size: %d bytes\n", len);

    if (len < 44 || len > 200000) {
      Serial.println("Invalid audio file size");
      http.end();
      state.isPlaying = false;
      return false;
    }

    WiFiClient* stream = http.getStreamPtr();
    
    // Safety padding for buffers to prevent heap corruption
    const size_t kHeaderSize = 44;
    const size_t kReadBufferSize = 1024;
    const size_t kPadding = 128;

    uint8_t* header = static_cast<uint8_t*>(malloc(kHeaderSize + kPadding));
    uint8_t* readBuffer = static_cast<uint8_t*>(malloc(kReadBufferSize + kPadding));

    if (header == nullptr || readBuffer == nullptr) {
      Serial.println("Failed to allocate memory for playback");
      if (header != nullptr) free(header);
      if (readBuffer != nullptr) free(readBuffer);
      http.end();
      state.isPlaying = false;
      return false;
    }

    // Initialize buffers
    memset(header, 0, kHeaderSize + kPadding);
    memset(readBuffer, 0, kReadBufferSize + kPadding);

    int headerRead = 0;
    while (headerRead < kHeaderSize && http.connected()) {
      const int available = stream->available();
      if (available > 0) {
        const int toRead = min(available, static_cast<int>(kHeaderSize - headerRead));
        const int bytesRead = stream->readBytes(&header[headerRead], toRead);
        headerRead += bytesRead;
      } else {
        delay(1);
      }
      yield();
    }

    if (headerRead < kHeaderSize) {
      Serial.println("Failed to read complete WAV header");
      free(header);
      free(readBuffer);
      http.end();
      state.isPlaying = false;
      return false;
    }

    const int16_t numChannels = header[22] | (header[23] << 8);
    const int32_t sampleRate = header[24] | (header[25] << 8) | (header[26] << 16) | (header[27] << 24);
    const int16_t bitsPerSample = header[34] | (header[35] << 8);

    Serial.printf("WAV: %d channels, %d Hz, %d bits\n", numChannels, sampleRate, bitsPerSample);

    if (numChannels < 1 || numChannels > 2 || (bitsPerSample != 16 && bitsPerSample != 8)) {
      Serial.println("Unsupported audio format");
      free(header);
      free(readBuffer);
      http.end();
      state.isPlaying = false;
      return false;
    }

    free(header);

    const float usPerSample = 1000000.0f / sampleRate;
    const int bytesPerSample = max(1, bitsPerSample / 8);
    const int bytesPerFrame = bytesPerSample * numChannels;

    int totalPlayed = 0;
    unsigned long lastWiFiYield = millis();
    unsigned long lastSampleTime = micros();

    Serial.println("Playing audio...");
    digitalWrite(Config::kLedRecPin, HIGH);

    unsigned long playbackStartTime = millis();
    const unsigned long maxPlaybackTime = 30000;

    while (http.connected() && totalPlayed < len - 44) {
      if (millis() - lastWiFiYield > 500) {
        lastWiFiYield = millis();
        if (WiFi.status() != WL_CONNECTED) {
          Serial.println("WiFi disconnected during playback, attempting to reconnect...");
          WiFi.reconnect();
          delay(200);
        }
        yield();
      }

      if (millis() - playbackStartTime > maxPlaybackTime) {
        Serial.println("Playback timeout reached");
        break;
      }

      const int available = stream->available();
      if (available > 0) {
        const int toRead = min(available, static_cast<int>(kReadBufferSize));
        const int bytesRead = stream->readBytes(readBuffer, toRead);

        if (bytesRead <= 0) {
          delay(1);
          continue;
        }

        const int framesAvailable = bytesRead / bytesPerFrame;

        for (int i = 0; i < framesAvailable; i++) {
          const int sampleOffset = i * bytesPerFrame;
          int16_t sample16 = 0;

          if (bitsPerSample == 16) {
            sample16 = static_cast<int16_t>((readBuffer[sampleOffset + 1] << 8) | readBuffer[sampleOffset]);
          } else {
            sample16 = static_cast<int16_t>((readBuffer[sampleOffset] - 128) << 8);
          }

          const uint8_t dacValue = static_cast<uint8_t>((static_cast<int32_t>(sample16) + 32768) >> 8);
          dacWrite(Config::kDac1Pin, dacValue);
          dacWrite(Config::kDac2Pin, dacValue);

          const unsigned long now = micros();
          const unsigned long elapsed = now - lastSampleTime;
          if (elapsed < static_cast<unsigned long>(usPerSample)) {
            delayMicroseconds(static_cast<unsigned long>(usPerSample) - elapsed);
          }
          lastSampleTime = micros();
          totalPlayed += bytesPerFrame;
        }
      } else {
        delay(1);
      }
    }

    free(readBuffer);
    Serial.println("Playback complete");
    digitalWrite(Config::kLedRecPin, LOW);
    digitalWrite(Config::kLedSysPin, HIGH);
  } else {
    Serial.printf("Failed to download TTS audio: %d\n", httpCode);
    blinkLed(Config::kLedRecPin, 3);
  }

  http.end();
  dacWrite(Config::kDac1Pin, 127);
  dacWrite(Config::kDac2Pin, 127);
  delay(100);

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected after playback");
    digitalWrite(Config::kLedSysPin, LOW);
  }

  const bool playbackSucceeded = (httpCode == HTTP_CODE_OK);
  state.isPlaying = false;
  return playbackSucceeded;
}
