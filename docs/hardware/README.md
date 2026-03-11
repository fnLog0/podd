# ESP32 + INMP441 Setup

Quick setup guide for ESP32 audio capture with INMP441 microphone.

## Hardware Needed

- ESP32 (any model)
- INMP441 MEMS microphone
- Jumper wires
- 3.3V power supply

## Wiring Diagram

| INMP441 Pin | ESP32 Pin |
| ----------- | --------- |
| VDD         | 3.3V      |
| GND         | GND       |
| SCK (BCLK)  | GPIO 14   |
| WS (LRCK)   | GPIO 15   |
| SD (DATA)   | GPIO 32   |
| L/R         | GND       |

## ESP32 Code

See `/esp32/esp32.ino` for the complete code.

### Key Configuration

```cpp
// Update these in esp32.ino:

// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Backend Server URL (your computer's IP)
const char* serverUrl = "http://192.168.1.100:3000/upload";

// Audio Settings
#define SAMPLE_RATE 16000
#define SECONDS 5
```

### Find Your Computer's IP

```bash
# Linux/Mac
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr "IPv4"
```

## Upload Code to ESP32

1. Open Arduino IDE
2. Open `/esp32/esp32.ino`
3. Update WiFi credentials and server URL
4. Click Verify (✓)
5. Click Upload (→)
6. Open Serial Monitor (115200 baud)

## Troubleshooting

### WiFi Not Connecting

- Check SSID/password are correct
- Try 2.4GHz WiFi (ESP32 doesn't support 5GHz)

### No Audio Detected

- Check wiring (especially GND connection)
- Ensure L/R pin is grounded
- Verify 3.3V power supply
- Speak louder/closer to microphone

### Upload Fails

- Ensure backend server is running (`pnpm server`)
- Check computer and ESP32 are on same network
- Verify server URL is correct
- Check firewall settings

## How It Works

1. ESP32 records 5 seconds of audio
2. Uploads to backend server via WiFi
3. Backend transcribes with Sarvam AI
4. Backend processes with Gemini AI
5. Returns results to ESP32 Serial Monitor
