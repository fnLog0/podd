# 04 – Calling Podd backend APIs

Use the JWT from [03-backend-auth.md](03-backend-auth.md) to send health data (vitals, food log, water, etc.) from the ESP32.

Base URL: `http://<BACKEND_HOST>:8000`. All requests below need:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

(unless noted).

## 1. Post vitals

- **URL:** `POST /api/vitals`
- **Body example:**

```json
{
  "blood_pressure_systolic": 120,
  "blood_pressure_diastolic": 80,
  "heart_rate": 72,
  "blood_sugar": 95.0,
  "temperature": 36.6,
  "weight_kg": 70.0
}
```

All fields are optional; send only what you have.

**ESP32 example:**

```cpp
void postVitals(int heartRate, float temp = 0, float weightKg = 0) {
  HTTPClient http;
  String url = "http://" + String(BACKEND_HOST) + ":" + String(BACKEND_PORT) + "/api/vitals";
  http.begin(url);
  http.addHeader("Authorization", "Bearer " + g_accessToken);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<256> doc;
  if (heartRate > 0) doc["heart_rate"] = heartRate;
  if (temp > 0)      doc["temperature"] = temp;
  if (weightKg > 0) doc["weight_kg"] = weightKg;
  String body;
  serializeJson(doc, body);

  int code = http.POST(body);
  Serial.printf("POST /api/vitals -> %d\n", code);
  http.end();
}
```

## 2. Post food log

- **URL:** `POST /api/food-logs`
- **Body example:**

```json
{
  "description": "Oatmeal",
  "calories": 200.0,
  "meal_type": "breakfast",
  "protein_g": 5.0,
  "carbs_g": 30.0,
  "fat_g": 3.0
}
```

Send only the fields you have; `meal_type` is e.g. `breakfast`, `lunch`, `dinner`, `snack`.

## 3. Post water log

- **URL:** `POST /api/tracking/water/log`
- **Body example:** `{ "amount_ml": 250 }` (or the schema your backend expects; check backend docs).

## 4. Get vitals / food logs

- **GET** `/api/vitals` – list vitals.
- **GET** `/api/food-logs` – list food logs.

Same as before: `Authorization: Bearer <access_token>`, then parse JSON response.

## 5. Generic POST helper

```cpp
int apiPost(const char* path, const char* jsonBody) {
  HTTPClient http;
  String url = "http://" + String(BACKEND_HOST) + ":" + String(BACKEND_PORT) + path;
  http.begin(url);
  http.addHeader("Authorization", "Bearer " + g_accessToken);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(jsonBody);
  http.end();
  return code;
}
```

Use it like:

```cpp
StaticJsonDocument<128> doc;
doc["heart_rate"] = 75;
doc["temperature"] = 36.5;
String body;
serializeJson(doc, body);
apiPost("/api/vitals", body.c_str());
```

## 6. Backend route summary

| Purpose       | Method | Path (typical)           |
|---------------|--------|--------------------------|
| Login         | POST   | `/api/auth/login`        |
| Refresh       | POST   | `/api/auth/refresh`      |
| Current user  | GET    | `/api/auth/me`           |
| Vitals        | POST   | `/api/vitals`            |
| Vitals list   | GET    | `/api/vitals`            |
| Food log      | POST   | `/api/food-logs`         |
| Food logs     | GET    | `/api/food-logs`         |
| Water log     | POST   | `/api/tracking/water/log` |
| Water history | GET    | `/api/tracking/water/history` |

Confirm paths in your backend (e.g. OpenAPI at `http://<host>:8000/docs`).

## 7. Next

- [05-hardware-sensors.md](05-hardware-sensors.md) – read sensors on the ESP32 and send data to these APIs.
