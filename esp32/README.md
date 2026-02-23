# ESP32 + Podd Backend

Connect an **ESP32 (38-pin)** to the Podd Health Assistant backend: send vitals, logs, and read data over WiFi using the REST API.

## Docs in this folder

| File | Description |
|------|-------------|
| [01-esp32-setup.md](01-esp32-setup.md) | ESP32 38-pin board, Arduino IDE / ESP-IDF, drivers |
| [02-wifi-connection.md](02-wifi-connection.md) | WiFi connection and HTTP client on ESP32 |
| [03-backend-auth.md](03-backend-auth.md) | Login, JWT token, and authenticated requests |
| [04-api-calls.md](04-api-calls.md) | Call backend APIs (vitals, food log, tracking) |
| [05-hardware-sensors.md](05-hardware-sensors.md) | Optional: sensors (heart rate, etc.) for health data |
| [06-step-by-step-checklist.md](06-step-by-step-checklist.md) | Short step-by-step checklist |

## Flow (high level)

1. **ESP32** connects to WiFi.
2. **Login** to Podd backend → get **JWT access token**.
3. **Send data** (e.g. vitals, water log) with `Authorization: Bearer <token>`.
4. **Refresh token** when access token expires.

## Backend base URL

- Local: `http://<your-pc-ip>:8000` (backend runs on port 8000).
- Replace `<your-pc-ip>` with the computer’s IP on the same network as the ESP32.

## Next step

Start with [01-esp32-setup.md](01-esp32-setup.md) to set up the board and toolchain.
