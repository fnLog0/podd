#pragma once

namespace Config {

static const char kSsid[] = "Airtel_Effortless";
static const char kPassword[] = "Kainaat@123";

static const char kServerUrl[] = "http://192.168.1.8:3000/upload";
static const char kAudioBaseUrl[] = "http://192.168.1.8:3000/audio/";

static constexpr int kI2sWsPin = 15;
static constexpr int kI2sSdPin = 16;
static constexpr int kI2sSckPin = 14;

static constexpr int kDac1Pin = 25;
static constexpr int kDac2Pin = 26;

static constexpr int kLedRecPin = 33;
static constexpr int kLedSysPin = 27;
static constexpr int kButtonPin = 4;

static constexpr int kSampleRate = 16000;
static constexpr int kSampleCount = 1024;
static constexpr int kRecordingSeconds = 2;
static constexpr unsigned long kLongPressMs = 2000;
static constexpr unsigned long kWifiCheckIntervalMs = 3000;
static constexpr unsigned long kDebounceDelayMs = 50;

}  // namespace Config
