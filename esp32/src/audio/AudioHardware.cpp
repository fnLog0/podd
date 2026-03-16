#include <Arduino.h>
#include <driver/i2s.h>

#include "../app/RuntimeConfig.h"
#include "AudioHardware.h"

bool initI2S() {
  Serial.println("Initializing I2S...");

  i2s_config_t i2sConfig = {};
  i2sConfig.mode = static_cast<i2s_mode_t>(I2S_MODE_MASTER | I2S_MODE_RX);
  i2sConfig.sample_rate = Config::kSampleRate;
  i2sConfig.bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT;
  i2sConfig.channel_format = I2S_CHANNEL_FMT_ONLY_LEFT;
  i2sConfig.communication_format = static_cast<i2s_comm_format_t>(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB);
  i2sConfig.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
  i2sConfig.dma_buf_count = 4; // Fewer, larger buffers for stability
  i2sConfig.dma_buf_len = 512; 
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
    return false;
  }

  result = i2s_set_pin(I2S_NUM_0, &pinConfig);
  if (result != ESP_OK) {
    Serial.printf("I2S pin config failed: %d\n", result);
    return false;
  }

  Serial.println("I2S initialized");
  return true;
}

void testDAC() {
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
}
