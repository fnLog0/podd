# ESP32 Firmware - Podd Audio Assistant

This firmware records short voice clips on ESP32, uploads them to a backend, then downloads and plays TTS audio.

## Clean Project Structure

```text
esp32/
├── esp32.ino
├── platformio.ini
├── src/
│   ├── app/
│   │   ├── ApplicationController.cpp/.h
│   │   ├── ApplicationState.h
│   │   ├── RuntimeConfig.h
│   │   └── DeviceUtilities.cpp/.h
│   ├── audio/
│   │   ├── AudioService.h
│   │   ├── RecordingWorkflow.cpp/.h
│   │   ├── AudioHardware.cpp/.h
│   │   ├── AudioUploader.cpp/.h
│   │   └── AudioPlayer.cpp/.h
│   └── connectivity/
│       └── WiFiService.cpp/.h
├── docs/
│   ├── ARDUINO_CLI_SETUP.md
│   ├── SETUP.md
│   └── WORKING_GUIDE.md
└── test-server/
```

## Notes

- Legacy simulation assets (`wokwi.toml`, `diagram.json`) and Wokwi-specific code paths were removed.
- The old `src/error` module was removed; modules now use direct success/failure flows.
- Dependency management remains unchanged (`ArduinoJson` via `platformio.ini`).

## Build

### Arduino CLI

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 .
```

### PlatformIO

```bash
pio run -e esp32dev
```
