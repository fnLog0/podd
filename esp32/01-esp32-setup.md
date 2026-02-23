# 01 – ESP32 38-pin setup

Set up your ESP32 (38-pin) and the toolchain so you can flash code and connect to the Podd backend.

## 1. ESP32 38-pin board

- Many “38-pin” boards are **ESP32-DevKitC** or **ESP32-WROOM-32** with 30 GPIOs + power/serial.
- Typical pins you’ll use:
  - **3V3, GND** – power
  - **TX, RX** – UART (USB‑serial)
  - **GPIO** – sensors, LEDs, etc. (see [05-hardware-sensors.md](05-hardware-sensors.md))

Identify your exact board (e.g. “ESP32 DevKit v1”) so you pick the right port and target in the IDE.

## 2. Install USB driver (Linux)

So the PC sees the ESP32 over USB:

```bash
# Ubuntu/Debian – often works without extra driver (CP210x / CH340)
sudo usbmodeswitch -v 0x10c4 -p 0xea60 2>/dev/null || true

# Add user to dialout so you can access serial without root
sudo usermod -aG dialout $USER
# Log out and back in (or reboot)
```

Check the device:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
# Example: /dev/ttyUSB0
```

## 3. Choose toolchain: Arduino IDE or PlatformIO

### Option A – Arduino IDE

1. **Install Arduino IDE** (from [arduino.cc](https://www.arduino.cc/en/software) or package manager).
2. **Add ESP32 board support:**
   - File → Preferences → “Additional Board Manager URLs”:
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Tools → Board → Boards Manager → search **“esp32”** → Install **“esp32 by Espressif Systems”**.
3. **Select board:**  
   Tools → Board → **ESP32 Arduino** → e.g. **“ESP32 Dev Module”** (or your exact 38-pin board).
4. **Select port:**  
   Tools → Port → `/dev/ttyUSB0` (or the port you saw above).

### Option B – PlatformIO (VS Code / CLI)

1. Install [VS Code](https://code.visualstudio.com/) and the **PlatformIO** extension.
2. New project:
   - PlatformIO: New Project
   - Board: e.g. **“ESP32 Dev Module”**
   - Framework: **Arduino**
3. Port: PlatformIO will list serial ports; use the one for your ESP32.

## 4. Test: blink sketch

1. Open **Blink** example:  
   File → Examples → 01.Basics → Blink (or in PlatformIO: Examples → Blink).
2. Change LED pin if needed (many ESP32 boards use **GPIO 2** for the built-in LED):

   ```cpp
   #define LED_BUILTIN 2
   ```

3. Upload and run. The onboard LED should blink.

## 5. Install libraries (for later steps)

In Arduino IDE: Sketch → Include Library → Manage Libraries. Install:

- **ArduinoJson** (e.g. v6.x or v7.x)
- **HTTPClient** / **WiFi** – usually already included with ESP32 core

In PlatformIO: add to `platformio.ini`:

```ini
lib_deps = bblanchon/ArduinoJson@^7.0.0
```

## 6. Next

- [02-wifi-connection.md](02-wifi-connection.md) – connect ESP32 to WiFi and do a simple HTTP GET.
