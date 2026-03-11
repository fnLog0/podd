# Zed + ESP32 + Wokwi Workflow

This project is best used with:

- `Zed` for editing code
- `arduino-cli` for compiling
- `VS Code + Wokwi` only when simulation is needed

## Project Folder

```text
/Users/nasimakhtar/Projects/fnlog0/podd/esp32
```

## 1. Edit in Zed

Open this folder in Zed and work normally.

Main files:

- `esp32.ino`
- `src/core`
- `src/audio`
- `src/network`

## 2. Compile for Real ESP32

Run:

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 --build-path /tmp/podd-esp32-build /Users/nasimakhtar/Projects/fnlog0/podd/esp32
```

## 3. Compile for Simulation Mode

Run:

```bash
arduino-cli compile --fqbn esp32:esp32:esp32 \
  --build-path /tmp/podd-esp32-sim-build \
  --build-property compiler.cpp.extra_flags=-DSIMULATION_MODE=1 \
  --build-property compiler.c.extra_flags=-DSIMULATION_MODE=1 \
  /Users/nasimakhtar/Projects/fnlog0/podd/esp32
```

## 4. Use Wokwi When You Need Simulation

Zed does not have an official Wokwi integration.

For simulation:

1. Open the same folder in VS Code
2. Install `PlatformIO IDE`
3. Install `Wokwi Simulator`
4. Use the `wokwi-esp32` environment
5. Start the simulator

## 5. Files Used by Wokwi

- `platformio.ini`
- `diagram.json`
- `wokwi.toml`

## Notes

- `Zed` is your editor
- `arduino-cli` is your build tool
- `VS Code + Wokwi` is only for simulator UI
- Wokwi will help with logic and networking flow, not full real audio hardware behavior
