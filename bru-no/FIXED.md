# Bruno Collection Fixed

## ✅ All 4 API Endpoints Detected

The Bruno collection now has all 4 API requests properly configured and auto-detected:

### Collection Structure
```
bru-no/
├── bruno.json           # Collection metadata
├── .bru               # Environment variables
├── health-check.bru    # ✅ GET / - Server health check
├── upload-audio-silent.bru   # ✅ POST /upload - Silent test
├── upload-audio-file.bru      # ✅ POST /upload - File upload test
└── download-audio.bru  # ✅ GET /audio/:filename - Download TTS
```

## 📋 API Endpoints

### 1. Health Check (GET /)
```http
GET {{baseUrl}}/
```
- Tests if server is running
- Returns server status and available endpoints

### 2. Upload Audio - Silent Test (POST /upload)
```http
POST {{baseUrl}}/upload
Content-Type: application/octet-stream
```
- Uploads silent audio for testing
- Returns transcription, AI response, and TTS audio path

### 3. Upload Audio - File Test (POST /upload)
```http
POST {{baseUrl}}/upload
Content-Type: application/octet-stream
```
- Uploads audio file from test-files/test-audio.wav
- Returns transcription, AI response, and TTS audio path

### 4. Download TTS Audio (GET /audio/:filename)
```http
GET {{baseUrl}}/audio/{{filename}}
```
- Downloads the TTS audio file
- Requires `filename` environment variable

## 🚀 How to Use

### Import Collection
1. Open Bruno application
2. Click "Import Collection"
3. Select `bru-no/` folder
4. Bruno will auto-detect all 4 API endpoints

### Configure Environment
1. In Bruno, click on "Environments"
2. Set variables:
   - `baseUrl`: `http://192.168.1.6:3000`
   - `filename`: TTS audio filename (for download test)

### Test Endpoints
1. **Health Check** - Run `health-check.bru` to verify server
2. **Upload Test** - Run either upload test to send audio
3. **Download Test** - Set `filename` variable and run download test

## ✅ Validation

```bash
pnpm run validate-bruno
```

Output:
```
✅ Collection directory exists
✅ bruno.json - Name: Audio Assistant API, Version: 1, Type: collection
✅ .bru - Environment configuration
✅ health-check.bru - Uses environment variables
✅ upload-audio-silent.bru - Uses environment variables
✅ upload-audio-file.bru - Uses environment variables
✅ download-audio.bru - Uses environment variables
✅ Collection is VALID
```

## 📝 Notes

- Bruno should now auto-detect all 4 API requests
- All requests use `{{baseUrl}}` environment variable
- Download request needs `{{filename}}` variable set
- Upload-file test references `../test-files/test-audio.wav`

## 🔧 Troubleshooting

### Still only 2 APIs showing?
1. Close Bruno completely
2. Delete Bruno's cache (Settings > Clear Cache)
3. Re-open Bruno
4. Re-import the collection

### Environment variables not working?
1. Click on "Environments" in Bruno
2. Select "local" environment
3. Ensure `baseUrl` is set to `http://192.168.1.6:3000`

### File upload not working?
1. Ensure `test-files/test-audio.wav` exists
2. Run `pnpm run generate-audio` if missing
3. Bruno needs to be able to access the file path
