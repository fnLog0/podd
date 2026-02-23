# 05 – Hardware and sensors (optional)

Use the ESP32’s GPIO and common sensors to collect health-related data and send it to the Podd backend via the APIs in [04-api-calls.md](04-api-calls.md).

## 1. ESP32 38-pin GPIO (short)

- **Safe to use:** e.g. GPIO 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33.
- **Avoid:** GPIO 0, 2 (boot/strapping), 6–11 (flash), 34–39 (input-only, no pullup).

Power sensors from **3V3** when possible; check each sensor’s datasheet.

## 2. Heart rate (e.g. MAX30102 / pulse sensor)

- **MAX30102:** I2C (SDA/SCL on your board, e.g. GPIO 21, 22).
- **Analog pulse sensor:** connect to an ADC pin (e.g. GPIO 34 or 35), read with `analogRead()`, then filter and detect peaks to estimate BPM.

Example (concept): read ADC in a loop, compute BPM, then:

```cpp
postVitals(bpm, 0, 0);  // heart_rate only
```

## 3. Temperature

- **DS18B20 (1-Wire):** one GPIO for data (with 4.7k pullup to 3V3). Use a 1-Wire library, read temperature, then send in `POST /api/vitals` as `temperature`.
- **DHT22 / DHT11:** one GPIO for data. Use DHT library; send `temperature` (and humidity if you store it).

## 4. Weight (load cell + HX711)

- **HX711:** data pin and clock pin to two GPIOs. Use HX711 library, calibrate, read weight in kg, then send as `weight_kg` in `POST /api/vitals`.

## 5. Buttons for simple logs

- **Water log:** one button → on press, send e.g. `POST` with `amount_ml: 250`.
- **Food / meal:** button or simple menu on a small display → send a predefined food log entry.

## 6. Wiring tips

- Use a common **GND** for ESP32 and all sensors.
- Keep I2C/1-Wire wires short; add pullups where the module doesn’t have them.
- If you use 5V sensors, use a level shifter or a 3V3-compatible part to avoid damaging the ESP32.

## 7. Data flow

1. Read sensor (e.g. `bpm`, `temp`, `weight_kg`).
2. Build JSON (see [04-api-calls.md](04-api-calls.md)).
3. Ensure you’re logged in and have a valid JWT.
4. `POST` to the right endpoint; on 401, refresh token and retry.

## 8. Next

- [06-step-by-step-checklist.md](06-step-by-step-checklist.md) – quick checklist from zero to “ESP32 sending data to Podd”.
