# Quick Start Guide

Get your ESP32 + INMP441 system running in 10 minutes.

## Step 1: Setup Backend (5 minutes)

```bash
# 1. Install dependencies
pnpm install

# 2. Create .env file
cp .env.example .env

# 3. Add your API keys to .env:
#    SARVAM_API_KEY=your_sarvam_api_key
#    GOOGLE_API_KEY=your_google_api_key

# 4. Start of server
pnpm server
```

Server will run on: http://localhost:3000

## Step 2: Setup ESP32 (5 minutes)

### Hardware Wiring

| INMP441 | ESP32   |
| ------- | ------- |
| VDD     | 3.3V    |
| GND     | GND     |
| SCK     | GPIO 14 |
| WS      | GPIO 15 |
| SD      | GPIO 32 |
| L/R     | GND     |

### Upload Code

1. Open Arduino IDE
2. Open `/esp32/esp32.ino`
3. Update these lines:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   const char* serverUrl = "http://YOUR_COMPUTER_IP:3000/upload";
   ```
4. Click Upload (→)

### Find Your Computer IP

```bash
# Linux/Mac
ifconfig | grep "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr "IPv4"
```

## Step 3: Test

1. Open Arduino IDE Serial Monitor (115200 baud)
2. Wait for "WiFi connected!"
3. Speak into microphone when recording starts
4. See results in Serial Monitor!

## Expected Output

**ESP32 Serial Monitor:**

```
WiFi connected!
Recording 5 seconds...
Uploading audio...
Server response: {"success":true,"transcript":"Hello how are you?","aiResponse":"I'm doing great!"}
```

**Backend Terminal:**

```
🚀 Server running on http://localhost:3000
📥 Received audio from ESP32
📊 Size: 32000 bytes
🚀 Starting multi-agent workflow...
📞 Agent 1: Transcribing audio...
✅ Transcription completed
🤖 Agent 2: Processing with AI...
✅ AI response generated
```

## Troubleshooting

| Problem               | Solution                         |
| --------------------- | -------------------------------- |
| WiFi not connecting   | Check SSID/password in esp32.ino |
| Server not responding | Check computer IP and firewall   |
| No audio detected     | Check wiring (especially GND)    |
| No transcript         | Check API keys in .env file      |

## Need More Details?

- [Hardware Setup Guide](hardware/README.md) - Full hardware documentation
- [Backend Setup Guide](backend_doc/README.md) - Full backend documentation
- [Main README](../README.md) - Project overview
