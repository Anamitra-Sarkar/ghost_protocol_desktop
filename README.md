# GHOST-PROTOCOL

<div align="center">

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗    ██████╗ ██████╗  ██████╗    ║
║    ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝    ██╔══██╗██╔══██╗██╔═══██╗   ║
║    ██║  ███╗███████║██║   ██║███████╗   ██║       ██████╔╝██████╔╝██║   ██║   ║
║    ██║   ██║██╔══██║██║   ██║╚════██║   ██║       ██╔═══╝ ██╔══██╗██║   ██║   ║
║    ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║       ██║     ██║  ██║╚██████╔╝   ║
║     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝       ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ║
║                                                                               ║
║                        R A M - O N L Y   V A U L T                            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

**A high-security, RAM-only encrypted vault application**

</div>

## Overview

GHOST-PROTOCOL is a CIA/NSA "Black Ops" style terminal application for storing highly classified notes. All data is encrypted with AES-256 and stored only in RAM - nothing ever touches the disk.

### Security Features

- **🔐 RAM-Only Storage**: All secrets are encrypted in memory. Nothing is written to disk.
- **👁️ Camera Sentinel**: Face detection monitors for unauthorized viewers.
  - **0 Faces**: Privacy shield engages (screen blur)
  - **1 Face**: Normal operation
  - **>1 Faces**: PANIC - Immediate memory wipe
- **🔑 Dead Man's Key**: USB drive authentication required.
  - App requires `GHOST_KEY` USB drive to start
  - Removing the USB triggers immediate memory wipe
- **⚠️ Panic Button**: Manual emergency wipe functionality
- **🛡️ Secure Memory Wipe**: Multi-pass overwrite with random data before clearing

## Requirements

- Python 3.10+
- Linux or Windows with webcam and USB ports
- Display capable of running GUI applications

## Installation

```bash
# Clone the repository
git clone https://github.com/Anamitra-Sarkar/ghost_protocol_desktop.git
cd ghost_protocol_desktop

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

- `customtkinter` - Modern high-DPI UI framework
- `opencv-python` - Computer vision for face detection
- `pycryptodome` - AES-256 encryption
- `psutil` - System monitoring (USB detection)
- `pillow` - Image processing

## Usage

### Normal Operation (Full Security)

1. Insert a USB drive labeled `GHOST_KEY`
2. Run the application:

```bash
python main.py
```

### Development Mode

For testing without USB key or camera:

```bash
# Bypass USB requirement (INSECURE)
python main.py --bypass-usb

# Disable camera monitoring
python main.py --no-camera

# Both
python main.py --bypass-usb --no-camera
```

## Interface

### Main Components

1. **Secret Text Area** - Multi-line encrypted note storage
2. **Status Panel** - Real-time security status:
   - `CAMERA: ARMED/LOCKED/BREACH`
   - `USB KEY: SECURE/NO KEY/REMOVED`
   - `THREAT: LOW/MEDIUM/CRITICAL`
3. **Panic Button** - Emergency manual wipe

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `ESC` | Emergency Wipe |
| `F1` | Toggle Camera |
| `F2` | Toggle USB Guard |

## Security Protocols

### Face Detection Logic

- Processes 1 frame every 0.5 seconds (optimized for performance)
- Uses Haar Cascade classifier for face detection
- Triggers are immediate and irreversible

### Memory Wipe Procedure

When panic is triggered (any method):

1. Security threads are stopped
2. Encryption key is overwritten 3x with random data
3. Encrypted data is overwritten 3x with random data
4. IV is overwritten 3x with random data
5. All variables are set to empty
6. Process is terminated with `os._exit(0)`

## Architecture

```
ghost_protocol_desktop/
├── main.py              # Entry point & application controller
├── gui.py               # CustomTkinter GUI components
├── security_threads.py  # Camera & USB monitoring
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── LICENSE             # Apache 2.0 License
```

## Aesthetics

The interface uses a "Stealth Mode" theme:
- **Background**: Deep Black (#0a0a0a)
- **Text**: Neon Green (#00ff41)
- **Alerts**: Warning Yellow (#ffcc00)
- **Panic**: Danger Red (#ff0040)

Console output is cinematic with detailed security logs:
```
[CRITICAL] ████ INTRUDER DETECTED ████
[CRITICAL] MULTIPLE FACES DETECTED. SHOULDER SURFER ALERT!
[CRITICAL] INITIATING PROTOCOL 0.
```

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

## Disclaimer

This is a demonstration/educational project. While it implements real security measures, it should not be used for actual classified information storage without thorough security review.

---

<div align="center">

**[CLASSIFIED] // GHOST-PROTOCOL v1.0 // [NOFORN]**

</div>
