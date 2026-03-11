# ESP32 Firmware - Podd Audio Assistant

This directory contains the ESP32 firmware for the Podd Audio Assistant.

The project uses the Arduino framework on ESP32 and is organized into small modules so the main sketch stays minimal.

## Overview

- Records voice from an INMP441 I2S microphone
- Uploads raw audio to a backend server over WiFi
- Downloads TTS audio from the backend
- Plays the response through ESP32 DAC pins and an external amplifier
- Uses LEDs and a push button for basic device control

## Project Structure

- `esp32.ino` - Thin Arduino entrypoint with `setup()` and `loop()`
- `src/core/AppController.cpp/.h` - App startup, button handling, and top-level flow
- `src/core/AppState.h` - Shared runtime state
- `src/core/Config.h` - Pins, timing values, WiFi, and backend URLs
- `src/core/SystemUtils.cpp/.h` - LED blink and reset helpers
- `src/audio/AudioManager.cpp/.h` - Recording, upload, download, and playback
- `src/network/WifiManager.cpp/.h` - WiFi setup, events, and reconnect logic
- `platformio.ini` - PlatformIO environments for hardware and simulation
- `diagram.json` - Wokwi circuit definition
- `wokwi.toml` - Wokwi firmware mapping

## Current Behavior

- Sample rate: `16000`
- Recording length: `2` seconds
- Short button press: start recording
- Long button press: reset device

Current runtime values come from `src/core/Config.h`.

## Hardware Wiring

### INMP441 I2S Microphone -> ESP32

```text
INMP441 Pin    ESP32 Pin    Notes
VDD            3.3V         Do not use 5V
GND            GND
SCK            GPIO 14      I2S BCLK
WS             GPIO 15      I2S LRCLK
SD             GPIO 16      I2S data in
L/R            GND          Left channel
```

### Amplifier / Speaker -> ESP32

```text
ESP32 Pin      Amplifier Pin    Notes
GPIO 25        Audio In (L)     DAC1 analog output
GPIO 26        Audio In (R)     DAC2 analog output
5V             VCC
GND            GND
```

GPIO `25` and `26` are DAC pins, not I2S output pins.

### LEDs

```text
GPIO 33 -> 220 ohm resistor -> recording LED -> GND
GPIO 27 -> 220 ohm resistor -> system LED -> GND
```

### Button

```text
GPIO 4 -> push button -> GND
```

The code uses `INPUT_PULLUP`, so no external pull-up resistor is required.

## Configuration

Update values in `src/core/Config.h` when needed.

Hardware mode uses:

- your normal WiFi SSID/password
- backend URLs like `http://192.168.x.x:3000/...`

Simulation mode uses:

- SSID: `Wokwi-GUEST`
- empty password
- backend URLs: `http://host.wokwi.internal:3000/...`

## Build Options

### Arduino IDE

1. Open `esp32.ino`
2. Select `Tools > Board > esp32 > ESP32 Dev Module`
3. Install the `esp32` board package
4. Install the `ArduinoJson` library
5. Compile or upload

### Arduino CLI

Normal build:

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 --build-path /tmp/podd-esp32-build /Users/nasimakhtar/Projects/fnlog0/podd/esp32
```

Simulation-mode build:

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 \
  --build-path /tmp/podd-esp32-sim-build \
  --build-property compiler.cpp.extra_flags=-DSIMULATION_MODE=1 \
  --build-property compiler.c.extra_flags=-DSIMULATION_MODE=1 \
  /Users/nasimakhtar/Projects/fnlog0/podd/esp32
```

### PlatformIO

Available environments in `platformio.ini`:

- `esp32dev` - real hardware
- `wokwi-esp32` - simulation build with `SIMULATION_MODE=1`

## Wokwi Simulation

The Wokwi setup is intended for logic and network testing, not full audio hardware validation.

What simulation covers:

- boot flow
- button handling
- LED behavior
- WiFi flow
- upload/download request flow

What simulation does not fully cover:

- real I2S microphone behavior
- real DAC speaker output

In simulation mode:

- microphone capture is replaced with generated sample data
- downloaded audio is not played through the DAC

### Wokwi Steps

1. Start your backend locally on port `3000`
2. Open this folder in VS Code with Wokwi support
3. Build the `wokwi-esp32` environment
4. Start the simulator
5. Press the virtual button to run a simulated request cycle

## Runtime Flow

1. Device boots
2. WiFi connects
3. System LED indicates ready state
4. Short button press starts a 2-second recording
5. Audio uploads to the backend
6. Backend response is parsed
7. TTS audio is downloaded
8. Audio is played on hardware builds, or skipped in simulation mode

## Troubleshooting

### Arduino IDE error: "Unable to handle compilation, expected exactly one compiler job in ''"

Try:

1. Close Arduino IDE and reopen the sketch folder
2. Make sure you opened `esp32.ino`, not an individual `.cpp` file
3. Re-select `ESP32 Dev Module`
4. Clear `~/Library/Caches/arduino`
5. Restart Arduino IDE and compile again

If Arduino IDE continues to fail, use `arduino-cli` or PlatformIO.

### Missing ArduinoJson

If build fails with `ArduinoJson.h: No such file or directory`, install the library:

```bash
arduino-cli lib install ArduinoJson
```

### Backend not reachable in Wokwi

Make sure:

- your backend is running on port `3000`
- you are using simulation mode
- requests are going to `host.wokwi.internal`

## Notes

- Keep the folder name as `esp32` if you use Arduino IDE or Arduino CLI. Arduino expects the sketch folder name to match `esp32.ino`.
- If you move files again, keep the root sketch small and update include paths carefully.
