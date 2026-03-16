#include <Arduino.h>
#include <WiFi.h>
#include <driver/i2s.h>

#include "../app/ApplicationState.h"
#include "../app/RuntimeConfig.h"
#include "../app/DeviceUtilities.h"
#include "AudioHardware.h"
#include "AudioUploader.h"
#include "AudioPlayer.h"

// THE DEFINITIVE STABILITY FIX: 
// Use a static global buffer instead of heap allocation.
// This removes the buffer from the heap entirely, making "Bad Tail" errors impossible.
#define MAX_AUDIO_SAMPLES (Config::kSampleRate * Config::kRecordingSeconds + 1024)
static int16_t g_audioBuffer[MAX_AUDIO_SAMPLES];

bool setupAudioHardware() {
  const bool initialized = initI2S();
  if (!initialized) {
    Serial.println("Audio hardware init failed");
    return false;
  }

  dacWrite(Config::kDac1Pin, 127);
  dacWrite(Config::kDac2Pin, 127);

  testDAC();

  Serial.println("Speaker test complete");
  delay(500);
  return true;
}

void startRecording(AppState& state) {
  if (state.isRecording) {
    Serial.println("Recording already in progress!");
    return;
  }

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, cannot record");
    blinkLed(Config::kLedRecPin, 3);
    return;
  }

  // Use the static global buffer instead of dynamic heap memory
  const int totalSamples = MAX_AUDIO_SAMPLES;
  int16_t* samples = g_audioBuffer;
  
  // Clear the static buffer
  memset(samples, 0, totalSamples * sizeof(int16_t));

  state.isRecording = true;
  digitalWrite(Config::kLedRecPin, HIGH);
  Serial.println("Recording started (Static Buffer Mode)...");

  size_t bytesReadThisTime = 0;
  int samplesActuallyRead = 0;

  for (int i = 0; i < totalSamples; i += Config::kSampleCount) {
    const int remaining = totalSamples - samplesActuallyRead;
    const size_t toRead = (remaining < Config::kSampleCount ? remaining : Config::kSampleCount) * sizeof(int16_t);

    if (toRead <= 0) break;

    esp_err_t err = i2s_read(I2S_NUM_0, &samples[samplesActuallyRead], toRead, &bytesReadThisTime, portMAX_DELAY);
    
    if (err == ESP_OK && bytesReadThisTime > 0) {
      samplesActuallyRead += bytesReadThisTime / sizeof(int16_t);
    }
    
    if (samplesActuallyRead >= totalSamples) break;
    if (i % 5000 == 0) { Serial.print("."); yield(); }
  }
  
  // Explicitly stop I2S to ensure DMA doesn't "clobber" memory in the background
  i2s_stop(I2S_NUM_0);

  Serial.println("\nRecording complete. Uploading...");
  digitalWrite(Config::kLedRecPin, LOW);

  if (WiFi.status() == WL_CONNECTED) {
    const size_t uploadSize = samplesActuallyRead * sizeof(int16_t);
    
    // We NO LONGER free 'samples' here because it's a static buffer
    const UploadResult uploadResult = uploadAudio(samples, uploadSize);
    const String ttsFilename = uploadResult.ttsFilename;
    const bool uploadSucceeded = uploadResult.success;

    Serial.printf("Memory: %d bytes free\n", ESP.getFreeHeap());

    if (uploadSucceeded && ttsFilename.length() > 0) {
      playTTSAudio(state, ttsFilename);
    }
  } else {
    blinkLed(Config::kLedSysPin, 3);
  }
  
  // Restart I2S for the next recording
  i2s_start(I2S_NUM_0);

  state.isRecording = false;
  Serial.println("\n========================================");
  Serial.println("Ready for next recording");
  Serial.println("Press button to record (2 seconds)");
  Serial.println("========================================\n");
}
