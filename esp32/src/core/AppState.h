#pragma once

struct AppState {
  bool isRecording = false;
  bool isPlaying = false;
  bool buttonPressed = false;
  unsigned long pressStartTime = 0;
  unsigned long lastWiFiCheck = 0;
};
