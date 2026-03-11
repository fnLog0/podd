# Podd ESP32 Test Server

This is a minimal local server for testing the ESP32 firmware.

## What It Does

- accepts raw PCM uploads on `POST /upload`
- saves uploaded audio into `uploads/`
- generates a small test WAV file in `audio/output/`
- returns JSON in the same shape expected by the ESP32 firmware
- serves WAV files from `GET /audio/output/<file>.wav`

## Run

```bash
cd /Users/nasimakhtar/Projects/fnlog0/podd/test-server
npm start
```

The server runs on port `3000` by default.

## ESP32 URLs

Point the ESP32 firmware to:

- upload: `http://YOUR_COMPUTER_IP:3000/upload`
- audio base: `http://YOUR_COMPUTER_IP:3000/audio/`

Update these values in:

- `/Users/nasimakhtar/Projects/fnlog0/podd/esp32/src/core/Config.h`

## Test Endpoints

- `GET /health`
- `POST /upload`
- `GET /audio/output/<file>.wav`

## Example Upload Test

```bash
curl -X POST http://localhost:3000/upload \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/path/to/file.pcm
```

## Notes

- no external npm dependencies are required
- generated WAV files are simple test tones
- this is only for local firmware testing
