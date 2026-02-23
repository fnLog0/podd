# 03 – Backend auth (login and JWT)

The Podd backend uses **JWT**: you login once, get an **access_token**, and send it in the `Authorization` header for protected APIs.

## 1. Login request

- **URL:** `POST /api/auth/login`
- **Body (JSON):** `email`, `password`
- **Response (JSON):** `access_token`, `refresh_token`, `token_type` (e.g. `"bearer"`)

Example with Arduino/ESP32:

```cpp
#include <ArduinoJson.h>

String login(const char* email, const char* password) {
  HTTPClient http;
  String url = "http://" + String(BACKEND_HOST) + ":" + String(BACKEND_PORT) + "/api/auth/login";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<128> req;
  req["email"]    = email;
  req["password"] = password;
  String body;
  serializeJson(req, body);

  int code = http.POST(body);
  String accessToken = "";
  if (code == 200) {
    StaticJsonDocument<512> doc;
    DeserializationError err = deserializeJson(doc, http.getString());
    if (!err) {
      accessToken = doc["access_token"].as<String>();
    }
  }
  http.end();
  return accessToken;
}
```

## 2. Store and use the access token

Keep the token in a global (or in NVS/EEPROM for persistence):

```cpp
String g_accessToken = "";

void setup() {
  // ... WiFi connect ...

  g_accessToken = login("user@example.com", "yourpassword");
  if (g_accessToken.length() > 0) {
    Serial.println("Logged in. Token: " + g_accessToken.substring(0, 20) + "...");
  } else {
    Serial.println("Login failed");
  }
}
```

## 3. Call a protected endpoint

Send the token in the header for every request to protected routes:

```cpp
void apiGetWithToken(const char* path) {
  if (g_accessToken.length() == 0) {
    Serial.println("Not logged in");
    return;
  }

  HTTPClient http;
  String url = "http://" + String(BACKEND_HOST) + ":" + String(BACKEND_PORT) + path;
  http.begin(url);
  http.addHeader("Authorization", "Bearer " + g_accessToken);

  int code = http.GET();
  Serial.printf("%s -> %d\n", path, code);
  if (code == 200) {
    Serial.println(http.getString());
  } else if (code == 401) {
    Serial.println("Unauthorized – token expired or invalid");
    // Trigger login again or use refresh_token (see below)
  }
  http.end();
}

// Example: get current user
apiGetWithToken("/api/auth/me");
```

## 4. Refresh token (when access token expires)

When you get **401 Unauthorized**, use the refresh token to get a new access token:

- **URL:** `POST /api/auth/refresh`
- **Body (JSON):** `refresh_token`
- **Response:** new `access_token` and `refresh_token`

```cpp
String g_refreshToken = "";

// In login(): also save g_refreshToken = doc["refresh_token"].as<String>();

bool refreshAccessToken() {
  if (g_refreshToken.length() == 0) return false;
  HTTPClient http;
  String url = "http://" + String(BACKEND_HOST) + ":" + String(BACKEND_PORT) + "/api/auth/refresh";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  StaticJsonDocument<256> req;
  req["refresh_token"] = g_refreshToken;
  String body;
  serializeJson(req, body);
  int code = http.POST(body);
  bool ok = false;
  if (code == 200) {
    StaticJsonDocument<512> doc;
    if (!deserializeJson(doc, http.getString())) {
      g_accessToken  = doc["access_token"].as<String>();
      g_refreshToken = doc["refresh_token"].as<String>();
      ok = true;
    }
  }
  http.end();
  return ok;
}
```

In your loop, if you get 401, call `refreshAccessToken()` and retry the request.

## 5. Summary

| Step | Action |
|------|--------|
| 1 | `POST /api/auth/login` with `email` and `password` |
| 2 | Save `access_token` (and optionally `refresh_token`) |
| 3 | Use header `Authorization: Bearer <access_token>` on all protected calls |
| 4 | On 401, use `POST /api/auth/refresh` with `refresh_token`, then retry |

## 6. Next

- [04-api-calls.md](04-api-calls.md) – send vitals, food log, water, etc. to the backend.
