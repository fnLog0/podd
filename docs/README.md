# Documentation

Simple documentation for Z PODD - Multi-Agent Audio Processing System.

## 🚀 Quick Start

**New to the project?** Start here: [Quick Start Guide](./QUICK_START.md) - Get running in 10 minutes!

## 📁 Documentation Structure

### [Hardware Setup](./hardware/)

ESP32 + INMP441 microphone hardware setup and configuration.

- Wiring diagrams
- ESP32 code configuration
- Troubleshooting

### [Backend Setup](./backend_doc/)

Node.js backend with Sarvam STT and Google Gemini AI.

- Installation and setup
- API endpoints
- Multi-agent workflow
- Troubleshooting

## 🚀 Quick Start

### Option 1: File-Based (Quick Test)

1. Setup backend
2. Place audio file as `./audio-sample.wav`
3. Run: `pnpm start`

### Option 2: ESP32 + Backend (Full System)

1. Setup hardware (see [Hardware Setup](./hardware/))
2. Setup backend (see [Backend Setup](./backend_doc/))
3. Run: `pnpm server`
4. ESP32 will automatically upload audio

## 📋 Workflow Overview

```
ESP32 + INMP441 → Backend Server → Sarvam STT → Gemini AI → Response
```

**Backend Processing:**

1. Receive audio from ESP32 (or use file)
2. Convert to WAV format
3. Transcribe with Sarvam AI
4. Process with Google Gemini AI
5. Return transcript and AI response

## 🛠️ System Requirements

**ESP32:**

- ESP32 microcontroller
- INMP441 microphone
- WiFi connection
- Arduino IDE

**Backend:**

- Node.js 18+
- pnpm
- Sarvam AI API key
- Google AI API key

## 📞 Need Help?

- Hardware issues → [Hardware Setup](./hardware/#troubleshooting)
- Backend issues → [Backend Setup](./backend_doc/#troubleshooting)
- Main project → [README](../README.md)

## 📝 Documentation Management

### Rules for Maintaining Documentation

**DO NOT create new documentation files** - Update existing files only!

### Where to Update for Future Changes

| Feature/Change             | Update Location              |
| -------------------------- | ---------------------------- |
| Hardware changes           | `docs/hardware/README.md`    |
| ESP32 code/configuration   | `docs/hardware/README.md`    |
| Backend API changes        | `docs/backend_doc/README.md` |
| New environment variables  | `docs/backend_doc/README.md` |
| Installation/Setup changes | `docs/backend_doc/README.md` |
| Workflow changes           | `docs/backend_doc/README.md` |
| Quick start steps          | `docs/QUICK_START.md`        |
| New getting started info   | `docs/QUICK_START.md`        |
| Overall project updates    | `../README.md`               |

### Documentation Structure (Fixed - Do Not Change)

```
docs/
├── hardware/README.md   - All hardware documentation
├── backend_doc/README.md - All backend documentation
├── QUICK_START.md      - Quick start guide
└── README.md           - This file (documentation index)
```

### When Adding New Features

1. **Update existing files** - Add content to appropriate existing doc
2. **Keep it simple** - One feature should not require multiple docs
3. **Remove outdated info** - Delete or update old content
4. **Update this table** - Add new feature types above

### Example: Adding New Hardware Sensor

❌ **WRONG:**

```
docs/hardware/new-sensor-README.md (new file)
```

✅ **CORRECT:**

```
docs/hardware/README.md (add new sensor section)
```

### Example: Adding New API Endpoint

❌ **WRONG:**

```
docs/api/new-endpoint.md (new file)
```

✅ **CORRECT:**

```
docs/backend_doc/README.md (add to API endpoints section)
```

### Documentation Updates Checklist

Before finishing any implementation:

- [ ] Updated `docs/hardware/README.md` if hardware changes
- [ ] Updated `docs/backend_doc/README.md` if backend changes
- [ ] Updated `docs/QUICK_START.md` if setup steps change
- [ ] Updated `../README.md` if project overview changes
- [ ] Removed outdated information
- [ ] Checked for broken links
- [ ] Ran `pnpm format` on all changed files

### Why This Structure?

**Simple & Maintainable:**

- Only 4 files to manage
- No duplicate information
- Easy to find where to update
- Reduces documentation debt

**Future-proof:**

- New features → existing files
- Updates → same location
- No file explosion
- Consistent structure

### Violations

If you find someone creating new documentation files:

1. Stop them
2. Ask why they can't use existing structure
3. Help them update the right file
4. Reference this section

Documentation simplicity is a project requirement.
