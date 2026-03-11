# ESP32 Hardware Connections - Podd Assistant

**Hardware Components:**
- ESP32S 38Pin Development Board (WIFI+BLUETOOTH) × 1
- INMP441 MEMS Microphone Module (I2S) × 1
- PAM8403 Digital Audio Amplifier Module × 1
- 0.5W 8 Ohm Speaker × 1
- Momentary Tactile Push Button Module × 1
- RGB LED 5mm with 2 pin (Auto Flashing) × 2

---

## Connection Diagram

### 1. INMP441 I2S Microphone → ESP32

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

---

### 2. PAM8403 Amplifier + Speaker → ESP32

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
- Use ESP32's built-in DAC functionality with PWM or analogWrite()

---

### 3. LEDs → ESP32

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

---

### 4. Push Button → ESP32 (RECOMMENDED: Internal Pull-up)

**Best Option: Using ESP32 Internal Pull-up (Simpler & Recommended)**
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
- More reliable for typical use cases

**Code Implementation:**
```cpp
#define BUTTON 4

void setup() {
  pinMode(BUTTON, INPUT_PULLUP);  // Enable internal pull-up resistor
}

void loop() {
  if (digitalRead(BUTTON) == LOW) {
    // Button pressed (pulled LOW to ground)
    delay(50);  // Simple debounce
    // Your button action here
  }
}
```

**Suggested Button Function:**
- Press to start/stop recording
- Long press (hold >2s) for system reset

---

## Summary Table

| Component       | ESP32 Pins Used         | Connection Type  |
|-----------------|-------------------------|------------------|
| INMP441 Mic     | 14, 15, 16, 3.3V, GND  | I2S              |
| PAM8403 Amp     | 25, 26, 5V, GND        | DAC (Analog)     |
| Speaker         | -                       | Analog           |
| LED1 (Rec)      | GPIO 33                 | Digital Out      |
| LED2 (Sys)      | GPIO 27                 | Digital Out      |
| Push Button     | GPIO 4                  | Digital In       |

---

## Critical Warnings ⚠️

1. **NEVER power INMP441 with 5V** - it will be permanently damaged! Use only 3.3V.
2. **PAM8403 requires analog input** - use DAC pins (25, 26), not I2S digital protocol.
3. **Ground connection is critical** - ensure all components share common ground.
4. **Speaker impedance** - Must use 4Ω-8Ω speaker with PAM8403 (0.5W max).

---

## Pin Summary Reference

### I2S Configuration (Microphone)
- `BCLK` = GPIO 14
- `LRCLK` = GPIO 15
- `DATA` = GPIO 16

### DAC Configuration (Speaker)
- `DAC1` = GPIO 25 (Left channel)
- `DAC2` = GPIO 26 (Right channel)

### GPIO Configuration
- `LED_REC` = GPIO 33 (Recording indicator)
- `LED_SYS` = GPIO 27 (System status)
- `BUTTON` = GPIO 4 (Control button)

---

## Recommended Software Configuration

### Arduino IDE Configuration

**For INMP441 (I2S Microphone):**
```cpp
#define I2S_WS 15
#define I2S_SD 16
#define I2S_SCK 14

// Setup I2S with these pins
```

**For PAM8403 (Analog DAC):**
```cpp
#define DAC1 25  // Left channel
#define DAC2 26  // Right channel

// Use dacWrite() or analogWrite()
```

**For LEDs:**
```cpp
#define LED_REC 33
#define LED_SYS 27

pinMode(LED_REC, OUTPUT);
pinMode(LED_SYS, OUTPUT);
```

**For Button:**
```cpp
#define BUTTON 4

pinMode(BUTTON, INPUT_PULLUP);

// Check button state (LOW = pressed)
if (digitalRead(BUTTON) == LOW) {
  // Button pressed
}
```

---

## Testing Checklist

- [ ] Power ESP32 with 5V (USB or external)
- [ ] Verify INMP441 receives 3.3V only
- [ ] Check all GND connections are common
- [ ] Test microphone with I2S code
- [ ] Test speaker with DAC code
- [ ] Test LEDs with digital write
- [ ] Test button with digital read
- [ ] Verify speaker volume (adjust in code if needed)

---

## Troubleshooting

### No Audio from Speaker
- Check PAM8403 is powered with 5V
- Verify DAC pins (25, 26) are not damaged
- Test speaker separately with known audio source
- Check for loose connections

### Microphone Not Working
- Verify INMP441 is powered with 3.3V (NOT 5V!)
- Check I2S pin connections (14, 15, 16)
- Ensure common ground between ESP32 and INMP441

### LEDs Not Lighting
- Check resistor value (220Ω recommended)
- Verify correct polarity (anode +, cathode -)
- Test GPIO with multimeter
- For auto-flashing LEDs, they need constant power

### Button Not Responding
- Verify INPUT_PULLUP mode in code
- Check button wiring
- Test with multimeter (should read HIGH when not pressed, LOW when pressed)
