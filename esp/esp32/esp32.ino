#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <driver/i2s.h>
#include <ArduinoJson.h>

// WiFi Credentials
const char* ssid = "Airtel_Effortless";
const char* password = "Kainaat@123";

// Backend Server
const char* serverUrl = "http://192.168.1.8:3000/upload";
const char* audioBaseUrl = "http://192.168.1.8:3000/audio/";

// I2S Configuration (Microphone)
#define I2S_WS 15   // Word Select / LRCK
#define I2S_SD 16   // Serial Data (FIXED: was 32, now 16 per hardware doc)
#define I2S_SCK 14  // Serial Clock / BCLK

// DAC Configuration (Speaker/Audio Output)
#define DAC1 25     // DAC1 for left channel
#define DAC2 26     // DAC2 for right channel

// GPIO Configuration
#define LED_REC 33  // Recording indicator (Red LED)
#define LED_SYS 27  // System status (Green LED)
#define BUTTON 4    // Control button

// Audio Configuration
#define SAMPLE_RATE 16000
#define SAMPLE_COUNT 1024
#define RECORDING_SECONDS 2  // Reduced from 3 to save memory for playback
#define LONG_PRESS_MS 2000  // 2 seconds for long press
#define WIFI_CHECK_INTERVAL 3000  // Check WiFi every 3 seconds
#define DEBOUNCE_DELAY_MS 50  // Button debounce delay

// Global state
bool isRecording = false;
bool isPlaying = false;
bool buttonPressed = false;
unsigned long pressStartTime = 0;
unsigned long lastWiFiCheck = 0;

// WiFi event handler
void WiFiEvent(WiFiEvent_t event, arduino_event_info_t info) {
  switch (event) {
    case ARDUINO_EVENT_WIFI_STA_CONNECTED:
      Serial.println("📡 WiFi connected to AP");
      break;
    case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
      Serial.println("⚠️ WiFi disconnected from AP");
      digitalWrite(LED_SYS, LOW);
      break;
    case ARDUINO_EVENT_WIFI_STA_GOT_IP:
      Serial.println("🌐 Got IP address");
      Serial.print("IP: ");
      Serial.println(WiFi.localIP());
      digitalWrite(LED_SYS, HIGH);
      break;
    default:
      break;
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting ESP32 Audio Assistant...");

  // Initialize GPIO
  Serial.println("Initializing GPIO...");
  pinMode(LED_REC, OUTPUT);
  pinMode(LED_SYS, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);
  pinMode(DAC1, OUTPUT);
  pinMode(DAC2, OUTPUT);

  // Initial LED state
  digitalWrite(LED_REC, LOW);
  digitalWrite(LED_SYS, LOW);

  // Small delay to let WiFi stack stabilize
  delay(100);

  // Configure WiFi for better stability
  WiFi.persistent(false);
  WiFi.onEvent(WiFiEvent);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.setSleep(false);

  // Connect to WiFi
  connectWiFi();

  // Initialize I2S for microphone
  initI2S();

  // Set DAC to neutral position (silence)
  dacWrite(DAC1, 127);
  dacWrite(DAC2, 127);

  // Test speaker with simple beep sequence
  Serial.println("🔊 Testing speaker...");
  for (int i = 0; i < 3; i++) {
    for (int j = 0; j < 10; j++) {
      dacWrite(DAC1, 200);
      dacWrite(DAC2, 200);
      delayMicroseconds(500);
      dacWrite(DAC1, 55);
      dacWrite(DAC2, 55);
      delayMicroseconds(500);
    }
    delay(100);
  }

  // Ensure DAC is properly silenced after test
  dacWrite(DAC1, 127);
  dacWrite(DAC2, 127);
  Serial.println("✅ Speaker test complete");
  delay(500);

  Serial.println("\n========================================");
  Serial.println("✅ System Ready!");
  Serial.printf("Memory: Free %d bytes, Heap %d bytes\n", ESP.getFreeHeap(), ESP.getHeapSize());
  Serial.println("Press button to record (2 seconds)");
  Serial.println("Hold button >2s for system reset");
  Serial.println("========================================\n");

  // Blink system LED to indicate ready
  blinkLED(LED_SYS, 3);
}

void loop() {
  // Periodically check WiFi connection
  unsigned long currentTime = millis();
  if (currentTime - lastWiFiCheck > WIFI_CHECK_INTERVAL) {
    lastWiFiCheck = currentTime;
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("⚠️ WiFi disconnected, reconnecting...");
      digitalWrite(LED_SYS, LOW);
      // Use WiFi.reconnect() for faster reconnection
      WiFi.reconnect();
      // Wait briefly for reconnect
      int retries = 0;
      while (WiFi.status() != WL_CONNECTED && retries < 10) {
        delay(500);
        retries++;
      }
      if (WiFi.status() == WL_CONNECTED) {
        digitalWrite(LED_SYS, HIGH);
        Serial.println("✅ WiFi reconnected!");
      } else {
        // If reconnect fails, try full connectWiFi
        connectWiFi();
      }
    }
  }

  // Check button state with debounce
  static unsigned long lastDebounceTime = 0;
  static int lastButtonState = HIGH;
  static int buttonState = HIGH;

  int currentButtonRead = digitalRead(BUTTON);

  // Debounce - only change state if stable for DEBOUNCE_DELAY_MS
  if (currentButtonRead != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > DEBOUNCE_DELAY_MS) {
    if (currentButtonRead != buttonState) {
      buttonState = currentButtonRead;

      if (buttonState == LOW && !buttonPressed) {
        // Button just pressed (stable)
        buttonPressed = true;
        pressStartTime = millis();
        Serial.println("Button pressed...");
      } else if (buttonState == HIGH && buttonPressed) {
        // Button just released (stable)
        buttonPressed = false;
        unsigned long pressDuration = millis() - pressStartTime;

        if (pressDuration > LONG_PRESS_MS) {
          // Long press - system reset
          Serial.println("Long press detected - Resetting system...");
          resetSystem();
        } else {
          // Short press - toggle recording
          if (!isRecording) {
            startRecording();
          } else {
            Serial.println("Recording in progress, please wait...");
          }
        }
      }
    }
  }

  lastButtonState = currentButtonRead;

  // Check for long press while holding
  if (buttonPressed && !isRecording) {
    unsigned long pressDuration = millis() - pressStartTime;
    if (pressDuration > LONG_PRESS_MS) {
      Serial.println("Long press detected - Release to reset...");
      blinkLED(LED_SYS, 1);
    }
  }

  delay(50);
}

void connectWiFi() {
  Serial.println("Connecting to WiFi...");

  // Don't disconnect if already connected
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("✅ Already connected to WiFi");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    digitalWrite(LED_SYS, HIGH);
    return;
  }

  // Properly clean up WiFi stack before reconnecting
  WiFi.mode(WIFI_OFF);
  delay(500);
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  delay(200);
  WiFi.setAutoReconnect(true);
  WiFi.setSleep(false);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    yield();
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");

    // System LED on solid when connected
    digitalWrite(LED_SYS, HIGH);
  } else {
    Serial.println("\n❌ WiFi connection failed!");
    // Blink system LED to indicate connection issue
    blinkLED(LED_SYS, 5);
  }
}

void initI2S() {
  Serial.println("Initializing I2S...");

  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 64,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };

  esp_err_t ret = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  if (ret != ESP_OK) {
    Serial.printf("❌ I2S driver install failed: %d\n", ret);
    return;
  }

  ret = i2s_set_pin(I2S_NUM_0, &pin_config);
  if (ret != ESP_OK) {
    Serial.printf("❌ I2S pin config failed: %d\n", ret);
    return;
  }

  Serial.println("✅ I2S initialized!");
}

void startRecording() {
  if (isRecording) {
    Serial.println("Recording already in progress!");
    return;
  }

  // Check WiFi before recording
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi not connected, cannot record");
    blinkLED(LED_REC, 3);
    return;
  }

  // Check available memory
  int totalSamples = SAMPLE_RATE * RECORDING_SECONDS;
  size_t bufferSize = totalSamples * sizeof(int16_t);
  Serial.printf("Need %d bytes, available: %d bytes\n", bufferSize, ESP.getFreeHeap());

  if (ESP.getFreeHeap() < bufferSize + 20000) {  // Extra 20KB margin
    Serial.println("❌ Not enough memory!");
    blinkLED(LED_REC, 3);
    return;
  }

  isRecording = true;
  Serial.println("========================================");
  Serial.println("🔴 Recording started...");
  Serial.println("========================================");

  // Turn on recording LED
  digitalWrite(LED_REC, HIGH);

  // Allocate buffer for recording (96KB for 3 seconds at 16kHz)
  int16_t* samples = (int16_t*)malloc(bufferSize);

  if (samples == NULL) {
    Serial.println("❌ Memory allocation failed!");
    isRecording = false;
    digitalWrite(LED_REC, LOW);
    return;
  }

  Serial.printf("Allocated %d bytes for %d samples\n", bufferSize, totalSamples);

  // Read audio from I2S with more frequent WiFi checks
  Serial.printf("Recording %d seconds...\n", RECORDING_SECONDS);
  size_t bytesRead;
  unsigned long lastWiFiCheck = millis();
  int samplesActuallyRead = 0;

  for (int i = 0; i < totalSamples; i += SAMPLE_COUNT) {
    i2s_read(I2S_NUM_0, &samples[i], SAMPLE_COUNT * sizeof(int16_t), &bytesRead, portMAX_DELAY);
    samplesActuallyRead += (bytesRead / sizeof(int16_t));

    // Show progress every 5k samples
    if (i % 5000 == 0) {
      Serial.print(".");

      // Check WiFi more frequently during recording
      if (millis() - lastWiFiCheck > 500) {
        lastWiFiCheck = millis();
        if (WiFi.status() != WL_CONNECTED) {
          Serial.println("\n⚠️ WiFi disconnected during recording!");
          free(samples);
          samples = NULL;
          isRecording = false;
          digitalWrite(LED_REC, LOW);
          return;
        }
      }
    }
  }

  Serial.println("\n✅ Recording complete!");
  Serial.printf("📊 Recorded %d samples\n", samplesActuallyRead);

  if (samplesActuallyRead < totalSamples * 0.8) {
    Serial.println("⚠️  Warning: Recorded fewer samples than expected");
  }

  // Turn off recording LED
  digitalWrite(LED_REC, LOW);

  // Upload to server
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("📤 Uploading audio to server...");
    String ttsFilename = uploadAudio(samples, bufferSize);

    // Free memory immediately after upload
    free(samples);
    samples = NULL;

    Serial.printf("Memory after upload: %d bytes free\n", ESP.getFreeHeap());

    // Small delay to let heap stabilize
    delay(100);

    // Play TTS response if available
    if (ttsFilename.length() > 0 && ttsFilename != "error") {
      Serial.println("🔊 Playing TTS response...");
      playTTSAudio(ttsFilename);
    }
  } else {
    Serial.println("❌ WiFi disconnected before upload");
    if (samples != NULL) {
      free(samples);
      samples = NULL;
    }
    blinkLED(LED_SYS, 3);
  }

  isRecording = false;
  Serial.println("\n========================================");
  Serial.println("✅ Ready for next recording!");
  Serial.println("Press button to record (2 seconds)");
  Serial.println("========================================\n");
}

String uploadAudio(int16_t* samples, size_t size) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi disconnected, cannot upload");
    return "error";
  }

  HTTPClient http;

  http.setTimeout(30000);

  if (!http.begin(serverUrl)) {
    Serial.println("❌ Failed to begin HTTP connection");
    return "error";
  }

  http.addHeader("Content-Type", "application/octet-stream");

  Serial.println("⏳ Sending data...");
  int httpCode = http.POST((uint8_t*)samples, size);

  String ttsFilename = "";

  if (httpCode > 0) {
    Serial.printf("✅ Server response code: %d\n", httpCode);

    String response = http.getString();
    Serial.println("📥 Server response:");
    Serial.println(response);

    http.end();

    if (response.length() < 10) {
      Serial.println("⚠️  Server response too small or empty");
      return "error";
    }

    DynamicJsonDocument doc(2048);
    DeserializationError error = deserializeJson(doc, response);

    if (!error && doc["success"]) {
      Serial.printf("📝 Transcript: %s\n", doc["transcript"].as<const char*>());
      Serial.printf("🤖 AI Response: %s\n", doc["aiResponse"].as<const char*>());

      if (doc.containsKey("ttsAudioPath")) {
        const char* ttsPath = doc["ttsAudioPath"];
        if (ttsPath != nullptr) {
          String pathStr(ttsPath);
          int lastSlash = pathStr.lastIndexOf('/');
          if (lastSlash != -1) {
            ttsFilename = pathStr.substring(lastSlash + 1);
          } else {
            ttsFilename = pathStr;
          }

          ttsFilename = "output/" + ttsFilename;
          Serial.printf("🎵 TTS Audio: %s\n", ttsFilename.c_str());
        } else {
          Serial.println("⚠️  TTS audio path is null");
        }
      } else {
        Serial.println("⚠️  No TTS audio path in response");
      }
    } else {
      Serial.println("⚠️  Failed to parse server response");
      if (error) {
        Serial.printf("⚠️  JSON error: %s\n", error.c_str());
      }
    }
  } else {
    Serial.printf("❌ Upload failed, error: %s\n", http.errorToString(httpCode).c_str());
    http.end();
  }

  return ttsFilename;
}

void playTTSAudio(String filename) {
  if (isPlaying) {
    Serial.println("Audio already playing...");
    return;
  }

  // Check WiFi before playback
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi disconnected, cannot play audio");
    blinkLED(LED_REC, 3);
    return;
  }

  // Check available memory before playback
  Serial.printf("Memory before playback: %d bytes free\n", ESP.getFreeHeap());
  if (ESP.getFreeHeap() < 30000) {
    Serial.println("❌ Not enough memory for audio playback");
    blinkLED(LED_REC, 3);
    return;
  }

  isPlaying = true;

  // Construct full URL
  String url = String(audioBaseUrl) + filename;
  Serial.printf("📡 Downloading TTS audio from: %s\n", url.c_str());

  // Retry mechanism for HTTP download
  HTTPClient http;
  int httpCode;
  int retryCount = 0;
  const int maxRetries = 3;

  do {
    // Set timeout to 60 seconds for download
    http.setTimeout(60000);

    if (!http.begin(url)) {
      Serial.println("❌ Failed to begin HTTP connection");
      retryCount++;
      if (retryCount < maxRetries) {
        Serial.printf("Retrying... (%d/%d)\n", retryCount + 1, maxRetries);
        delay(1000);
        continue;
      }
      isPlaying = false;
      return;
    }

    httpCode = http.GET();

    if (httpCode == HTTP_CODE_OK) {
      break;  // Success
    } else {
      Serial.printf("❌ HTTP GET failed: %d\n", httpCode);
      http.end();
      retryCount++;
      if (retryCount < maxRetries) {
        Serial.printf("Retrying... (%d/%d)\n", retryCount + 1, maxRetries);
        delay(1000);
        // Check and reconnect WiFi if needed
        if (WiFi.status() != WL_CONNECTED) {
          Serial.println("Reconnecting WiFi...");
          WiFi.reconnect();
          delay(500);
        }
      } else {
        Serial.println("❌ Max retries reached");
        isPlaying = false;
        return;
      }
    }
  } while (retryCount < maxRetries);

  if (httpCode == HTTP_CODE_OK) {
    int len = http.getSize();
    Serial.printf("📊 Audio size: %d bytes\n", len);

    if (len < 44 || len > 200000) {
      Serial.println("❌ Invalid audio file size");
      http.end();
      isPlaying = false;
      return;
    }

    WiFiClient* stream = http.getStreamPtr();

    // Allocate buffers on heap to avoid stack overflow
    uint8_t* header = (uint8_t*)malloc(44);
    uint8_t* readBuffer = (uint8_t*)malloc(1024);

    if (header == NULL || readBuffer == NULL) {
      Serial.println("❌ Failed to allocate memory for playback");
      if (header) free(header);
      if (readBuffer) free(readBuffer);
      http.end();
      isPlaying = false;
      return;
    }

    int headerRead = 0;
    while (headerRead < 44 && http.connected()) {
      int available = stream->available();
      if (available > 0) {
        int toRead = min(available, 44 - headerRead);
        int bytesRead = stream->readBytes(&header[headerRead], toRead);
        headerRead += bytesRead;
      } else {
        delay(1);
      }
      yield();
    }

    if (headerRead < 44) {
      Serial.println("❌ Failed to read complete WAV header");
      free(header);
      free(readBuffer);
      http.end();
      isPlaying = false;
      return;
    }

    int16_t numChannels = (header[22] | (header[23] << 8));
    int32_t sampleRate = header[24] | (header[25] << 8) | (header[26] << 16) | (header[27] << 24);
    int16_t bitsPerSample = header[34] | (header[35] << 8);

    Serial.printf("🎵 WAV: %d channels, %d Hz, %d bits\n", numChannels, sampleRate, bitsPerSample);

    if (numChannels < 1 || numChannels > 2 || (bitsPerSample != 16 && bitsPerSample != 8)) {
      Serial.println("❌ Unsupported audio format");
      free(header);
      free(readBuffer);
      http.end();
      isPlaying = false;
      return;
    }

    free(header);

    float usPerSample = 1000000.0 / sampleRate;
    int bytesPerSample = max(1, bitsPerSample / 8);
    int bytesPerFrame = bytesPerSample * numChannels;

    int totalPlayed = 0;
    unsigned long lastWiFiYield = millis();

    Serial.println("🔊 Playing audio...");
    digitalWrite(LED_REC, HIGH);

    unsigned long lastSampleTime = micros();

    while (http.connected() && totalPlayed < len - 44) {
      // Check WiFi stability periodically
      if (millis() - lastWiFiYield > 500) {
        lastWiFiYield = millis();
        if (WiFi.status() != WL_CONNECTED) {
          Serial.println("⚠️ WiFi disconnected during playback, attempting to reconnect...");
          // Attempt to reconnect without interrupting playback if possible
          WiFi.reconnect();
          delay(200);
        }
        yield();
      }

      int available = stream->available();
      if (available > 0) {
        int toRead = min(available, 1024);
        int bytesRead = stream->readBytes(readBuffer, toRead);

        int framesAvailable = bytesRead / bytesPerFrame;

        for (int i = 0; i < framesAvailable; i++) {
          int sampleOffset = i * bytesPerFrame;
          int16_t sample16;

          if (bitsPerSample == 16) {
            sample16 = (int16_t)((readBuffer[sampleOffset + 1] << 8) | readBuffer[sampleOffset]);
          } else {
            sample16 = (int16_t)(((readBuffer[sampleOffset] - 128) << 8));
          }

          uint8_t dacValue = (uint8_t)(((int32_t)sample16 + 32768) >> 8);

          dacWrite(DAC1, dacValue);
          dacWrite(DAC2, dacValue);

          unsigned long now = micros();
          unsigned long elapsed = now - lastSampleTime;
          if (elapsed < usPerSample) {
            delayMicroseconds(usPerSample - elapsed);
          }
          lastSampleTime = micros();

          totalPlayed += bytesPerFrame;
        }
      } else {
        delay(1);
      }
    }

    free(readBuffer);

    Serial.println("✅ Playback complete!");
    digitalWrite(LED_REC, LOW);
    digitalWrite(LED_SYS, HIGH);
  } else {
    Serial.printf("❌ Failed to download TTS audio: %d\n", httpCode);
    blinkLED(LED_REC, 3);
  }

  http.end();

  // Silence the DAC
  dacWrite(DAC1, 127);
  dacWrite(DAC2, 127);

  // Small delay to let WiFi stack stabilize after playback
  delay(100);

  // Ensure WiFi is still connected
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi disconnected after playback");
    digitalWrite(LED_SYS, LOW);
  }

  isPlaying = false;
}

void resetSystem() {
  Serial.println("🔄 Resetting system...");
  blinkLED(LED_SYS, 5);
  delay(1000);
  ESP.restart();
}

void blinkLED(int pin, int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(100);
    digitalWrite(pin, LOW);
    delay(100);
  }
}
