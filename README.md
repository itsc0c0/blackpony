# ■ BLACK PONY

```
██████  ██       █████   ██████ ██   ██     ██████   ██████  ███    ██ ██    ██
██   ██ ██      ██   ██ ██      ██  ██      ██   ██ ██    ██ ████   ██  ██  ██
██████  ██      ███████ ██      █████       ██████  ██    ██ ██ ██  ██   ████
██   ██ ██      ██   ██ ██      ██  ██      ██      ██    ██ ██  ██ ██    ██
██████  ███████ ██   ██  ██████ ██   ██     ██       ██████  ██   ████    ██
```

**Portable RF pentest toolkit with a fullscreen 8-bit pixel-art GUI.**  
Built with PyQt5. Real hardware access via `spidev` and `RPi.GPIO` — no simulations.

---

## Features

### NRF24 Module
- **SCAN** — Sweeps all 126 channels (2.400–2.525 GHz) using the RPD (Received Power Detector) register. Detects active devices and logs channel activity.
- **SNIFF** — Promiscuous-style packet capture with CRC disabled. Prints raw packets as hex in real time.
- **SWEEP** — Transmits noise payload at PA MAX + 2MBPS across all channels continuously.

### Jammer Module *(independent menu)*
- **WiFi Deauth** — 802.11 deauthentication flood via `airmon-ng` + `aireplay-ng`
- **BT/BLE Flood** — Randomized BLE advertisement flood via `hcitool`

> ⚠️ **For use only on your own devices and networks. Authorized security research only.**

---

## Requirements

```
Raspbian (Bookworm or Bullseye)
Python 3.9+
PyQt5
spidev
RPi.GPIO
aircrack-ng       (for WiFi Deauth)
bluez / hcitool   (for BT Flood)
```

---

## Installation

### 1. Enable SPI
```bash
sudo raspi-config nonint do_spi 0
sudo reboot
```

### 2. Run the installer
```bash
git clone https://github.com/USERNAME/blackpony
cd blackpony
sudo bash install.sh
```

### 3. Set up Python environment
```bash
sudo bash setup_complete.sh
```

### 4. If RF24 fails to install
```bash
sudo bash rf24_fix.sh
```

### 5. Launch
```bash
blackpony
```

---

## Auto-start on Boot (Raspbian Desktop)

```bash
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
```

Add at the bottom:
```
@blackpony
```

---

## File Structure

```
blackpony/
├── main.py              # Main application (PyQt5)
├── install.sh           # Full dependency installer
├── setup_complete.sh    # Python venv + environment setup
├── rf24_fix.sh          # RF24 troubleshooter (7 methods)
└── index.html           # Project website
```

---

## UI Preview

```
┌─────────────────────────┐
│ ✕  ■ BLACK PONY  00:00  │
│─────────────────────────│
│  > SELECT MODULE_       │
│ ┌──────────┐┌──────────┐│
│ │ ▓▓       ││ ▓▓       ││
│ │ NRF24    ││ JAMMER   ││
│ │Scan/Sniff││WiFi / BT ││
│ └──────────┘└──────────┘│
│ ┌──────────┐┌──────────┐│
│ │ ░░  GSM  ││ ░░  GPS  ││
│ │  (soon)  ││  (soon)  ││
│ └──────────┘└──────────┘│
└─────────────────────────┘
```

---

## License

MIT License — Use only for ethical and legal purposes.

---

*Black Pony v5.0 — direct hardware access via spidev + RPi.GPIO*
