# 06 – Step-by-step checklist

Short checklist to connect your **ESP32 (38-pin)** to the **Podd backend**.

---

## On your PC (Linux)

- [ ] **1.** Backend runs and is reachable on the network:
  ```bash
  cd /path/to/podd/backend
  source .venv/bin/activate
  uvicorn src.main:app --host 0.0.0.0 --port 8000
  ```
- [ ] **2.** Note your PC’s IP (e.g. `192.168.1.100`):
  ```bash
  ip -4 addr show | grep inet
  ```
- [ ] **3.** Optional: test from PC:
  ```bash
  curl http://localhost:8000/
  curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"email":"user@example.com","password":"yourpass"}'
  ```

---

## ESP32 setup

- [ ] **4.** USB driver and port: plug ESP32, run `ls /dev/ttyUSB* /dev/ttyACM*`, add user to `dialout` if needed.
- [ ] **5.** Arduino IDE or PlatformIO: ESP32 board support installed, board “ESP32 Dev Module” (or your 38-pin board) selected, correct port selected.
- [ ] **6.** Libraries: **ArduinoJson** (and any sensor libs you need).

---

## WiFi and backend URL

- [ ] **7.** In code: set `WIFI_SSID`, `WIFI_PASSWORD`.
- [ ] **8.** In code: set `BACKEND_HOST` to your PC IP (e.g. `192.168.1.100`), `BACKEND_PORT = 8000`.

---

## Auth

- [ ] **9.** Create a user (if needed): from PC, `POST /api/auth/register` with email, password, name; or use an existing account.
- [ ] **10.** In ESP32: call `POST /api/auth/login` with email and password; save `access_token` (and optionally `refresh_token`).
- [ ] **11.** For every protected request: add header `Authorization: Bearer <access_token>`.

---

## Sending data

- [ ] **12.** Test a protected endpoint: e.g. `GET /api/auth/me` with the Bearer token.
- [ ] **13.** Send vitals: `POST /api/vitals` with JSON body (e.g. `heart_rate`, `temperature`, `weight_kg`).
- [ ] **14.** If you get **401**: use `POST /api/auth/refresh` with `refresh_token`, get new `access_token`, then retry.

---

## Optional (sensors)

- [ ] **15.** Wire sensor (e.g. heart rate, temperature, load cell) to safe GPIOs.
- [ ] **16.** Read value in loop, build JSON, then `POST` to the right API (vitals, food log, water, etc.).

---

## Quick reference

| What        | URL / action |
|------------|------------------|
| Backend root | `GET http://<IP>:8000/` |
| Login      | `POST /api/auth/login` → body: `email`, `password` |
| Refresh    | `POST /api/auth/refresh` → body: `refresh_token` |
| Protected  | Header: `Authorization: Bearer <access_token>` |
| Vitals     | `POST /api/vitals` → body: e.g. `heart_rate`, `temperature`, `weight_kg` |

---

For details, see the other guides in this folder (README → 01–05).
