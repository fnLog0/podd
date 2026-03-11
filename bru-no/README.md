# Bruno API Testing Collection

This folder contains a complete Bruno API testing collection for the Audio Assistant API with **4 auto-detectable API endpoints**.

## 📦 Collection Files

```
bru-no/
├── bruno.json           # ✅ Collection metadata
├── .bru               # ✅ Environment variables
├── health-check.bru    # ✅ Health Check API
├── upload-audio-silent.bru   # ✅ Upload Silent API
├── upload-audio-file.bru      # ✅ Upload File API
├── download-audio.bru  # ✅ Download TTS API
├── README.md          # This file
└── FIXED.md           # Fix summary and details
```

## 🚀 Quick Start

### 1. Import Collection
```
Open Bruno → Import Collection → Select bru-no/ folder
```

### 2. Configure Environment
Set variables in Bruno:
- `baseUrl`: `http://192.168.1.6:3000`
- `filename`: TTS audio filename (for download)

### 3. Validate
```bash
pnpm run validate-bruno
```

## 📋 API Endpoints (All 4 Auto-Detected)

| File | Method | Endpoint | Purpose |
|------|---------|-----------|---------|
| `health-check.bru` | GET | `/` | Check server status |
| `upload-audio-silent.bru` | POST | `/upload` | Upload silent test audio |
| `upload-audio-file.bru` | POST | `/upload` | Upload audio file |
| `download-audio.bru` | GET | `/audio/:filename` | Download TTS response |

## 🧪 Testing Workflow

1. **Health Check** → Verify server is running
2. **Upload Test** → Send audio to server
3. **Copy TTS filename** → From upload response
4. **Download Test** → Get TTS audio file

## ✅ Status

- ✅ All 4 API endpoints detected by Bruno
- ✅ Environment variables configured
- ✅ Collection validation passing
- ✅ Clean structure, no unwanted files

## 📚 Documentation

- See `FIXED.md` for detailed fix information
- See `../BRUNO_STATUS.md` for full collection status
