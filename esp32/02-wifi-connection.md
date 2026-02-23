# 02 – WiFi and HTTP client

Connect the ESP32 to your WiFi and send a simple HTTP request (e.g. to the Podd backend root).

## 1. WiFi credentials

Define your network (later you can move these to a config file or EEPROM):

```cpp
const char* WIFI_SSID     = "YourNetworkName";
const char* WIFI_PASSWORD = "YourPassword";
```

## 2. Minimal sketch: connect and HTTP GET

```cpp
#include <WiFi.h>
#include <HTTPClient.h>

const char* WIFI_SSID     = "YourNetworkName";
const char* WIFI_PASSWORD = "YourPassword";

// Backend running on same network (use your PC's IP, port 8000)
const char* BACKEND_HOST = "192.168.1.100";  // Change this
const int   BACKEND_PORT = 8000;

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected. IP: " + WiFi.localIP().toString());
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected");
    delay(5000);
    return;
  }

  HTTPClient http;
  String url = "http://" + String(BACKEND_HOST) + ":" + String(BACKEND_PORT) + "/";
  http.begin(url);
  int code = http.GET();

  if (code > 0) {
    Serial.printf("GET %s -> %d\n", url.c_str(), code);
    Serial.println(http.getString());
  } else {
    Serial.printf("GET failed: %s\n", http.errorToString(code).c_str());
  }
  http.end();

  delay(10000);  // Every 10 seconds
}
```

## 3. Find your backend PC IP (Linux)

On the machine running the Podd backend:

```bash
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v 127.0.0.1
```

Use that IP for `BACKEND_HOST` (e.g. `192.168.1.100`). Ensure the backend is running:

```bash
cd backend && source .venv/bin/activate && uvicorn src.main:app --host 0.0.0.0 --port 8000
```

`--host 0.0.0.0` allows requests from the LAN (including ESP32).

## 4. Test

1. Upload the sketch.
2. Open Serial Monitor at **115200** baud.
3. You should see “Connected” and then JSON like `{"name":"Podd Health Assistant","version":"0.1.0"}` every 10 seconds.

## 5. HTTPS (optional)

If the backend is served over HTTPS, use:

```cpp
#include <WiFiClientSecure.h>
WiFiClientSecure client;
client.setInsecure();  // or set CA cert for production
http.begin(client, "https://your-server.com");
```

For local LAN, HTTP is usually enough.

## 6. Next

- [03-backend-auth.md](03-backend-auth.md) – login and use JWT for protected endpoints.
