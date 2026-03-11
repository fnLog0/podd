#include <Arduino.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <WiFi.h>
#include <driver/i2s.h>

#include "AudioManager.h"
#include "../core/Config.h"
#include "../core/SystemUtils.h"

namespace {

#if defined(SIMULATION_MODE)
void fillSimulatedSamples(int16_t* samples, int totalSamples) {
  for (int i = 0; i < totalSamples; i++) {
    const int phase = i % 64;
    samples[i] = phase < 32 ? 12000 : -12000;
  }
}
#endif

void initI2S() {
  Serial.println("Initializing I2S...");

  i2s_config_t i2sConfig = {};
  i2sConfig.mode = static_cast<i2s_mode_t>(I2S_MODE_MASTER | I2S_MODE_RX);
  i2sConfig.sample_rate = Config::kSampleRate;
  i2sConfig.bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT;
  i2sConfig.channel_format = I2S_CHANNEL_FMT_ONLY_LEFT;
  i2sConfig.communication_format = I2S_COMM_FORMAT_I2S;
  i2sConfig.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
  i2sConfig.dma_buf_count = 8;
  i2sConfig.dma_buf_len = 64;
  i2sConfig.use_apll = false;
  i2sConfig.tx_desc_auto_clear = false;
  i2sConfig.fixed_mclk = 0;

  i2s_pin_config_t pinConfig = {};
  pinConfig.bck_io_num = Config::kI2sSckPin;
  pinConfig.ws_io_num = Config::kI2sWsPin;
  pinConfig.data_out_num = I2S_PIN_NO_CHANGE;
  pinConfig.data_in_num = Config::kI2sSdPin;

  esp_err_t result = i2s_driver_install(I2S_NUM_0, &i2sConfig, 0, nullptr);
  if (result != ESP_OK) {
    Serial.printf("I2S driver install failed: %d\n", result);
    return;
  }

  result = i2s_set_pin(I2S_NUM_0, &pinConfig);
  if (result != ESP_OK) {
    Serial.printf("I2S pin config failed: %d\n", result);
    return;
  }

  Serial.println("I2S initialized");
}

String uploadAudio(int16_t* samples, size_t size) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, cannot upload");
    return "error";
  }

  HTTPClient http;
  http.setTimeout(30000);

  if (!http.begin(Config::kServerUrl)) {
    Serial.println("Failed to begin HTTP connection");
    return "error";
  }

  http.addHeader("Content-Type", "application/octet-stream");

  Serial.println("Sending data...");
  const int httpCode = http.POST(reinterpret_cast<uint8_t*>(samples), size);
  String ttsFilename;

  if (httpCode > 0) {
    Serial.printf("Server response code: %d\n", httpCode);

    const String response = http.getString();
    Serial.println("Server response:");
    Serial.println(response);
    http.end();

    if (response.length() < 10) {
      Serial.println("Server response too small or empty");
      return "error";
    }

    DynamicJsonDocument doc(2048);
    const DeserializationError error = deserializeJson(doc, response);

    if (!error && doc["success"]) {
      Serial.printf("Transcript: %s\n", doc["transcript"].as<const char*>());
      Serial.printf("AI Response: %s\n", doc["aiResponse"].as<const char*>());

      if (doc.containsKey("ttsAudioPath")) {
        const char* ttsPath = doc["ttsAudioPath"];
        if (ttsPath != nullptr) {
          String pathStr(ttsPath);
          const int lastSlash = pathStr.lastIndexOf('/');
          ttsFilename = lastSlash != -1 ? pathStr.substring(lastSlash + 1) : pathStr;
          ttsFilename = "output/" + ttsFilename;
          Serial.printf("TTS Audio: %s\n", ttsFilename.c_str());
        } else {
          Serial.println("TTS audio path is null");
        }
      } else {
        Serial.println("No TTS audio path in response");
      }
    } else {
      Serial.println("Failed to parse server response");
      if (error) {
        Serial.printf("JSON error: %s\n", error.c_str());
      }
    }
  } else {
    Serial.printf("Upload failed, error: %s\n", http.errorToString(httpCode).c_str());
    http.end();
  }

  return ttsFilename;
}

void playTTSAudio(AppState& state, const String& filename) {
  if (state.isPlaying) {
    Serial.println("Audio already playing...");
    return;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, cannot play audio");
    blinkLED(Config::kLedRecPin, 3);
    return;
  }

  Serial.printf("Memory before playback: %d bytes free\n", ESP.getFreeHeap());
  if (ESP.getFreeHeap() < 30000) {
    Serial.println("Not enough memory for audio playback");
    blinkLED(Config::kLedRecPin, 3);
    return;
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
      return;
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
      return;
    }
  } while (retryCount < maxRetries);

  if (httpCode == HTTP_CODE_OK) {
    const int len = http.getSize();
    Serial.printf("Audio size: %d bytes\n", len);

    if (len < 44 || len > 200000) {
      Serial.println("Invalid audio file size");
      http.end();
      state.isPlaying = false;
      return;
    }

    WiFiClient* stream = http.getStreamPtr();
    uint8_t* header = static_cast<uint8_t*>(malloc(44));
    uint8_t* readBuffer = static_cast<uint8_t*>(malloc(1024));

    if (header == nullptr || readBuffer == nullptr) {
      Serial.println("Failed to allocate memory for playback");
      if (header != nullptr) {
        free(header);
      }
      if (readBuffer != nullptr) {
        free(readBuffer);
      }
      http.end();
      state.isPlaying = false;
      return;
    }

    int headerRead = 0;
    while (headerRead < 44 && http.connected()) {
      const int available = stream->available();
      if (available > 0) {
        const int toRead = min(available, 44 - headerRead);
        const int bytesRead = stream->readBytes(&header[headerRead], toRead);
        headerRead += bytesRead;
      } else {
        delay(1);
      }
      yield();
    }

    if (headerRead < 44) {
      Serial.println("Failed to read complete WAV header");
      free(header);
      free(readBuffer);
      http.end();
      state.isPlaying = false;
      return;
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
      return;
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

      const int available = stream->available();
      if (available > 0) {
        const int toRead = min(available, 1024);
        const int bytesRead = stream->readBytes(readBuffer, toRead);
        const int framesAvailable = bytesRead / bytesPerFrame;

#if defined(SIMULATION_MODE)
        totalPlayed += bytesRead;
#else
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
#endif
      } else {
        delay(1);
      }
    }

    free(readBuffer);

#if defined(SIMULATION_MODE)
    Serial.println("Simulation mode: audio stream downloaded, DAC playback skipped");
#endif
    Serial.println("Playback complete");
    digitalWrite(Config::kLedRecPin, LOW);
    digitalWrite(Config::kLedSysPin, HIGH);
  } else {
    Serial.printf("Failed to download TTS audio: %d\n", httpCode);
    blinkLED(Config::kLedRecPin, 3);
  }

  http.end();
#if !defined(SIMULATION_MODE)
  dacWrite(Config::kDac1Pin, 127);
  dacWrite(Config::kDac2Pin, 127);
#endif
  delay(100);

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected after playback");
    digitalWrite(Config::kLedSysPin, LOW);
  }

  state.isPlaying = false;
}

}  // namespace

void setupAudioHardware() {
#if defined(SIMULATION_MODE)
  Serial.println("Simulation mode enabled: skipping I2S and DAC hardware init");
  Serial.println("Audio capture will use synthetic samples");
  return;
#else
  initI2S();

  dacWrite(Config::kDac1Pin, 127);
  dacWrite(Config::kDac2Pin, 127);

  Serial.println("Testing speaker...");
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 10; j++) {
      dacWrite(Config::kDac1Pin, 200);
      dacWrite(Config::kDac2Pin, 200);
      delayMicroseconds(500);
      dacWrite(Config::kDac1Pin, 55);
      dacWrite(Config::kDac2Pin, 55);
      delayMicroseconds(500);
    }
    delay(100);
  }

  dacWrite(Config::kDac1Pin, 127);
  dacWrite(Config::kDac2Pin, 127);
  Serial.println("Speaker test complete");
  delay(500);
#endif
}

void startRecording(AppState& state) {
  if (state.isRecording) {
    Serial.println("Recording already in progress!");
    return;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, cannot record");
    blinkLED(Config::kLedRecPin, 3);
    return;
  }

  const int totalSamples = Config::kSampleRate * Config::kRecordingSeconds;
  const size_t bufferSize = totalSamples * sizeof(int16_t);
  Serial.printf("Need %d bytes, available: %d bytes\n", static_cast<int>(bufferSize), ESP.getFreeHeap());

  if (ESP.getFreeHeap() < bufferSize + 20000) {
    Serial.println("Not enough memory!");
    blinkLED(Config::kLedRecPin, 3);
    return;
  }

  state.isRecording = true;
  Serial.println("========================================");
  Serial.println("Recording started...");
  Serial.println("========================================");
  digitalWrite(Config::kLedRecPin, HIGH);

  int16_t* samples = static_cast<int16_t*>(malloc(bufferSize));
  if (samples == nullptr) {
    Serial.println("Memory allocation failed!");
    state.isRecording = false;
    digitalWrite(Config::kLedRecPin, LOW);
    return;
  }

  Serial.printf("Allocated %d bytes for %d samples\n", static_cast<int>(bufferSize), totalSamples);
  Serial.printf("Recording %d seconds...\n", Config::kRecordingSeconds);

  size_t bytesRead = 0;
  unsigned long lastWiFiCheck = millis();
  int samplesActuallyRead = 0;

#if defined(SIMULATION_MODE)
  fillSimulatedSamples(samples, totalSamples);
  samplesActuallyRead = totalSamples;
  Serial.println("Generated synthetic audio samples for simulation");
#else
  for (int i = 0; i < totalSamples; i += Config::kSampleCount) {
    i2s_read(I2S_NUM_0, &samples[i], Config::kSampleCount * sizeof(int16_t), &bytesRead, portMAX_DELAY);
    samplesActuallyRead += bytesRead / sizeof(int16_t);

    if (i % 5000 == 0) {
      Serial.print(".");

      if (millis() - lastWiFiCheck > 500) {
        lastWiFiCheck = millis();
        if (WiFi.status() != WL_CONNECTED) {
          Serial.println("\nWiFi disconnected during recording!");
          free(samples);
          state.isRecording = false;
          digitalWrite(Config::kLedRecPin, LOW);
          return;
        }
      }
    }
  }
#endif

  Serial.println("\nRecording complete");
  Serial.printf("Recorded %d samples\n", samplesActuallyRead);
  if (samplesActuallyRead < totalSamples * 0.8) {
    Serial.println("Warning: Recorded fewer samples than expected");
  }

  digitalWrite(Config::kLedRecPin, LOW);

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Uploading audio to server...");
    const String ttsFilename = uploadAudio(samples, bufferSize);

    free(samples);
    samples = nullptr;

    Serial.printf("Memory after upload: %d bytes free\n", ESP.getFreeHeap());
    delay(100);

    if (ttsFilename.length() > 0 && ttsFilename != "error") {
      Serial.println("Playing TTS response...");
      playTTSAudio(state, ttsFilename);
    }
  } else {
    Serial.println("WiFi disconnected before upload");
    free(samples);
    samples = nullptr;
    blinkLED(Config::kLedSysPin, 3);
  }

  state.isRecording = false;
  Serial.println("\n========================================");
  Serial.println("Ready for next recording");
  Serial.println("Press button to record (2 seconds)");
  Serial.println("========================================\n");
}
