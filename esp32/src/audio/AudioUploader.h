#pragma once

struct UploadResult {
  bool success;
  String ttsFilename;
};

UploadResult uploadAudio(int16_t* samples, size_t size);
