# ESP32 Firmware - Podd Audio Assistant

This directory contains ESP32 firmware for the Podd Audio Assistant with voice interaction capabilities.

## Features

- 🎤 **Audio Recording**: I2S microphone (INMP441) for high-quality voice capture
- 🔊 **Audio Playback**: DAC output with PAM8403 amplifier for TTS responses
- 🔴 **Status LEDs**: Visual feedback for recording and system status
- 🔘 **Button Control**: Intuitive press-to-record interface
- 📡 **WiFi Connectivity**: Upload audio to backend server and download TTS responses
- 🤖 **Voice AI Integration**: Works with Sarvam STT and Gemini AI backend

## Files

- `esp32.ino` - Main firmware with complete audio capture and playback
- `platformio.ini` - PlatformIO configuration (alternative method)

## Hardware Setup

### INMP441 I2S Microphone → ESP32

```
INMP441 Pin    ESP32 Pin    Notes
────────────────────────────────────────────────────
VDD      ────── 3.3V        ⚠️ NOT 5V! Will damage mic!
GND      ────── GND
SCK      ────── GPIO 14     I2S0 Bit Clock (BCLK)
WS       ────── GPIO 15     I2S0 Word Select (LRCLK)
SD       ────── GPIO 16     I2S0 Serial Data (DATA)
L/R      ────── GND         Left channel selected
```

✅ **These connections are CORRECT**

### PAM8403 Amplifier + Speaker → ESP32

```
ESP32 Pin       PAM8403 Pin      Notes
────────────────────────────────────────────────────
GPIO 25   ────── Audio In (L)    DAC1 output (analog)
GPIO 26   ────── Audio In (R)    DAC2 output (analog)

PAM8403 Pin     Speaker Pin      Notes
────────────────────────────────────────────────────
L_OUT+   ────── Speaker +
L_OUT-   ────── Speaker -

ESP32 Power     PAM8403 Power    Notes
────────────────────────────────────────────────────
5V       ────── VCC
GND      ────── GND
```

⚠️ **IMPORTANT NOTE:**

- GPIO 25 and GPIO 26 are ESP32's **DAC channels** (DAC1, DAC2), **NOT I2S pins**
- PAM8403 is an **ANALOG amplifier**, it accepts analog input (0-3.3V AC)
- DO NOT use I2S protocol with PAM8403 directly
- Use ESP32's built-in DAC functionality with `dacWrite()`

### LEDs → ESP32

**LED1 (Recording Indicator - Red):**

```
ESP32 GPIO 33 ──► 220Ω resistor ──► LED1 Anode (+)
                                      │
                                      ▼
                                   GND (LED1 Cathode -)
```

**LED2 (System Status - Green):**

```
ESP32 GPIO 27 ──► 220Ω resistor ──► LED2 Anode (+)
                                      │
                                      ▼
                                   GND (LED2 Cathode -)
```

✅ **These connections are CORRECT**

**Note:** Auto-flashing LEDs will flash automatically when powered, so you may want to control them with software instead.

### Push Button → ESP32

**Using ESP32 Internal Pull-up (Recommended):**

```
ESP32 GPIO 4  ──► Button Pin 1
                    │
                   GND (Button Pin 2)
```

✅ **Why this is best:**

- Simpler wiring (only 2 connections)
- No extra components needed
- Built-in 30-50kΩ pull-up is sufficient for button input
- Standard practice for ESP32 projects

**Button Functions:**

- **Short Press (<2s)**: Start/stop recording (5 seconds duration)
- **Long Press (>2s)**: System reset

## Summary Table

| Component   | ESP32 Pins Used       | Connection Type |
| ----------- | --------------------- | --------------- |
| INMP441 Mic | 14, 15, 16, 3.3V, GND | I2S             |
| PAM8403 Amp | 25, 26, 5V, GND       | DAC (Analog)    |
| Speaker     | -                     | Analog          |
| LED1 (Rec)  | GPIO 33               | Digital Out     |
| LED2 (Sys)  | GPIO 27               | Digital Out     |
| Push Button | GPIO 4                | Digital In      |

## Configuration

**IMPORTANT:** WiFi credentials are already configured in `esp32.ino`:

```cpp
const char* ssid = "Airtel_Effortless";                    // ✅ Configured
const char* password = "Kainaat@123";                      // ✅ Configured
const char* serverUrl = "http://192.168.1.6:3000/upload";  // ✅ Correct IP
const char* audioBaseUrl = "http://192.168.1.6:3000/audio/"; // ✅ Correct IP
```

⚠️ **Update these values only if:**

- Your WiFi network name or password changes
- Your computer's IP address changes
- You're setting up on a different network

**Current configuration matches server at 192.168.1.6**

### Find Your Computer's IP

```bash
# Ubuntu/Linux (Simple)
hostname -I

# Linux/Mac (Detailed)
ip addr show | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr "IPv4"
```

**Note:** Use the IP that starts with 192.168.x.x (not 172.17.x.x or 172.18.x.x - those are internal/Docker)

## Upload Instructions

### Method 1: Arduino IDE (Recommended for Beginners)

1. **Install Arduino IDE**
   - Download from [arduino.cc](https://www.arduino.cc/en/software)
   - Install and open

2. **Install ESP32 Board Support**
   - File → Preferences
   - Add to "Additional Board Manager URLs":
     ```
     https://dl.espressif.com/dl/package_esp32_index.json
     ```
   - Click OK

3. **Install ESP32 Board**
   - Tools → Board → Boards Manager
   - Search "esp32"
   - Install "esp32 by Espressif Systems" (version 2.0.14 or later)
   - **Important:** Do NOT use version 3.0.0+ if you encounter issues

4. **Install ArduinoJson Library**
   - Tools → Manage Libraries
   - Search "ArduinoJson"
   - Install "ArduinoJson by Benoit Blanchon" (version 6.x)

5. **Select Board Settings**
   - Tools → Board → esp32 → **ESP32 Dev Module**
   - Tools → Port → Select your ESP32 port (e.g., /dev/ttyUSB0 or COM3)
   - Tools → Upload Speed → **921600** (faster) or **115200** (more stable)

6. **Open Sketch**
   - File → Open
   - Navigate to this folder and select `esp32.ino`

7. **Upload**
   - Click the Upload button (→)
   - Wait for "Done uploading" message

### Method 2: PlatformIO (Alternative)

**If using VS Code with PlatformIO extension:**

1. Install PlatformIO extension in VS Code
2. Open this folder in VS Code
3. PlatformIO will automatically detect `platformio.ini`
4. Click the arrow icon (→) in the bottom status bar to upload

## Usage

### Startup Sequence

1. Power on ESP32
2. System initializes WiFi, I2S, GPIO
3. **Green LED blinks 3 times** → System ready
4. **Green LED stays solid** → WiFi connected

### Recording Voice

1. **Press the button** briefly (< 2 seconds)
2. **Red LED turns ON** → Recording starts
3. Speak clearly into the microphone (5 seconds)
4. **Red LED turns OFF** → Recording complete
5. Audio uploads to server automatically
6. **Green LED blinks** → Processing response
7. **Green LED turns OFF** → Audio plays through speaker
8. **Green LED returns to solid** → Ready for next recording

### System Reset

1. **Hold the button** for more than 2 seconds
2. **Green LED blinks rapidly**
3. Release button
4. System restarts automatically

## Troubleshooting

### Error: "Unable to handle compilation, expected exactly one compiler job in ''"

This error occurs when Arduino IDE has conflicts. Try these solutions:

**Solution 1: Disable PlatformIO Extension (if using Arduino IDE)**

1. Close Arduino IDE
2. If you have PlatformIO VS Code extension installed, disable it temporarily
3. Open Arduino IDE again
4. Try compiling again

**Solution 2: Verify Board Selection**

1. Ensure you have selected a board: Tools → Board → esp32 → ESP32 Dev Module
2. Check that a port is selected: Tools → Port
3. If no port appears, try unplugging and replugging ESP32

**Solution 3: Clean Build**

1. Sketch → Show Sketch Folder
2. Delete the `build` folder if it exists
3. Restart Arduino IDE
4. Try compiling again

**Solution 4: Downgrade ESP32 Core (if needed)**

1. Tools → Board → Boards Manager
2. Search "esp32"
3. Click on "esp32 by Espressif Systems"
4. Select version 2.0.14 (not 3.x)
5. Install and try again

**Solution 5: Use PlatformIO Instead**
If Arduino IDE continues to have issues, use PlatformIO:

- Install VS Code
- Install PlatformIO extension
- Open this folder in VS Code
- Click the upload arrow in the bottom bar

### Upload Fails

**Problem:** Upload hangs or fails

**Solutions:**

1. Press BOOT button when "Connecting...." appears
2. Try lower upload speed (115200 instead of 921600)
3. Try a different USB cable (use data cable, not charge-only)
4. Check port selection

### WiFi Not Connecting

**Problem:** "WiFi connection failed!"

**Solutions:**

1. Verify SSID and password are correct
2. Use 2.4GHz network (5GHz may not work)
3. Check ESP32 is in WiFi range
4. Green LED will blink 5 times on connection failure

### No Audio Captured

**Problem:** Upload succeeds but no transcription

**Solutions:**

1. Check INMP441 wiring (especially GND)
2. Ensure L/R pin is connected to GND
3. Verify 3.3V power supply (NOT 5V!)
4. Speak closer to microphone
5. Check I2S pin assignments (14, 15, 16)

### No TTS Audio Playback

**Problem:** AI response received but no sound from speaker

**Solutions:**

1. Check PAM8403 is powered with 5V
2. Verify DAC pins (25, 26) connections
3. Test speaker separately with known audio source
4. Check speaker is 4Ω-8Ω (0.5W max)
5. Verify TTS audio file was generated on server

### LEDs Not Working

**Problem:** LEDs not lighting up

**Solutions:**

1. Check resistor value (220Ω recommended)
2. Verify correct polarity (anode +, cathode -)
3. Test GPIO with multimeter
4. For auto-flashing LEDs, they need constant power

### Button Not Responding

**Problem:** Button press doesn't trigger recording

**Solutions:**

1. Verify INPUT_PULLUP mode in code
2. Check button wiring
3. Test with multimeter (should read HIGH when not pressed, LOW when pressed)
4. Ensure button is connected to GPIO 4

## Expected Serial Monitor Output

### Startup

```
Starting ESP32 Audio Assistant...
Initializing GPIO...
Connecting to WiFi...
...
✅ WiFi connected!
IP address: 192.168.1.100
Initializing I2S...
✅ I2S initialized!

========================================
✅ System Ready!
Press button to record (5 seconds)
Hold button >2s for system reset
========================================
```

### Recording Session

```
Button pressed...
========================================
🔴 Recording started...
========================================
Recording 5 seconds...
.....
✅ Recording complete!
📊 Recorded 80000 samples
📤 Uploading audio to server...
⏳ Sending data...
✅ Server response code: 200
📥 Server response:
{
  "success": true,
  "transcript": "Hello, how are you?",
  "aiResponse": "I'm doing great! How can I help?",
  "ttsAudioPath": "/tts-output/response_1234567890.wav"
}
📝 Transcript: Hello, how are you?
🤖 AI Response: I'm doing great! How can I help?
🎵 TTS Audio: response_1234567890.wav
📡 Downloading TTS audio from: http://192.168.1.6:3000/audio/response_1234567890.wav
📊 Audio size: 32000 bytes
🔊 Playing audio...
✅ Playback complete!

========================================
✅ Ready for next recording!
Press button to record
========================================
```

## Critical Warnings ⚠️

1. **NEVER power INMP441 with 5V** - it will be permanently damaged! Use only 3.3V.
2. **PAM8403 requires analog input** - use DAC pins (25, 26), not I2S digital protocol.
3. **Ground connection is critical** - ensure all components share common ground.
4. **Speaker impedance** - Must use 4Ω-8Ω speaker with PAM8403 (0.5W max).
5. **DAC output voltage** - ESP32 DAC outputs 0-3.3V analog signal. Don't exceed this.

## Dependencies

- `WiFi.h` - ESP32 WiFi library
- `HTTPClient.h` - HTTP client for uploads/downloads
- `driver/i2s.h` - I2S audio interface
- `ArduinoJson.h` - JSON parsing for server responses

## Pin Summary Reference

### I2S Configuration (Microphone)

- `BCLK` = GPIO 14
- `LRCLK` = GPIO 15
- `DATA` = GPIO 16

### DAC Configuration (Speaker)

- `DAC1` = GPIO 25 (Left channel)
- `DAC2` = GPIO 26 (Right channel)

### GPIO Configuration

- `LED_REC` = GPIO 33 (Recording indicator - Red)
- `LED_SYS` = GPIO 27 (System status - Green)
- `BUTTON` = GPIO 4 (Control button)

## Audio Format

- **Sample Rate**: 16000 Hz
- **Channels**: Mono
- **Bit Depth**: 16-bit
- **Recording Duration**: 5 seconds per press

## Support

For more help:

- See main project README
- Check docs/backend_doc/ for detailed API documentation
- Review hardware connections in docs/backend_doc/HARDWARE_CONNECTIONS.md
