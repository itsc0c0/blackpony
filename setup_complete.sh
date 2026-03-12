#!/bin/bash

# ╔══════════════════════════════════════╗
# ║     BLACK PONY — SETUP COMPLETE     ║
# ║     MouseJack + venv fix            ║
# ╚══════════════════════════════════════╝

GREEN='\033[0;32m'; RED='\033[0;31m'
YELLOW='\033[1;33m'; CYAN='\033[0;36m'
WHITE='\033[1;37m'; DIM='\033[0;90m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}[✓]${NC} $1"; }
err()  { echo -e "  ${RED}[✗]${NC} $1"; }
info() { echo -e "  ${CYAN}[*]${NC} $1"; }
warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }
sep()  { echo -e "  ${DIM}────────────────────────────────────────${NC}"; }

clear
echo -e "${CYAN}"
echo "  ██████  ██       █████   ██████ ██   ██     ██████   ██████  ███    ██ ██    ██"
echo "  ██   ██ ██      ██   ██ ██      ██  ██      ██   ██ ██    ██ ████   ██  ██  ██ "
echo "  ██████  ██      ███████ ██      █████       ██████  ██    ██ ██ ██  ██   ████  "
echo "  ██   ██ ██      ██   ██ ██      ██  ██      ██      ██    ██ ██  ██ ██    ██   "
echo "  ██████  ███████ ██   ██  ██████ ██   ██     ██       ██████  ██   ████    ██   "
echo -e "${NC}"
echo -e "${CYAN}  ════════════════════════════════════════${NC}"
echo -e "${YELLOW}        SETUP COMPLETE v1.0              ${NC}"
echo -e "${CYAN}  ════════════════════════════════════════${NC}"
echo ""

# Root kontrolü
if [ "$EUID" -ne 0 ]; then
    err "Root gerekli: sudo bash setup_complete.sh"
    exit 1
fi

# Sabit env yolu
ENV_PATH="/home/koray/bp_env"
ok "venv yolu: $ENV_PATH"
echo ""

# ─────────────────────────────────────
# 1. venv oluştur / kontrol et
# ─────────────────────────────────────
echo -e "${WHITE}  [1/5] VENV${NC}"; sep

if [ ! -d "$ENV_PATH" ]; then
    info "venv oluşturuluyor: $ENV_PATH"
    sudo -u koray python3 -m venv "$ENV_PATH" --system-site-packages
    ok "venv oluşturuldu"
else
    ok "venv zaten mevcut: $ENV_PATH"
fi

# venv pip ile pyrf24 kur
info "pyrf24 kuruluyor..."
"$ENV_PATH/bin/pip" install pyrf24 --no-cache-dir 2>&1 | tail -3

if "$ENV_PATH/bin/python3" -c "import pyrf24" 2>/dev/null; then
    ok "pyrf24 kuruldu"
else
    warn "pyrf24 kurulamadı — sweep spidev ile çalışmaya devam eder"
fi
echo ""

# ─────────────────────────────────────
# 2. MouseJack kur
# ─────────────────────────────────────
echo -e "${WHITE}  [2/5] MOUSEJACK${NC}"; sep

if [ -f "/opt/blackpony/mousejack/mousejack.py" ]; then
    ok "MouseJack zaten kurulu"
else
    info "MouseJack indiriliyor..."
    cd /opt/blackpony

    if git clone --depth=1 https://github.com/BastilleResearch/mousejack 2>&1 | tail -2; then
        ok "MouseJack indirildi"
    else
        err "MouseJack indirilemedi — internet bağlantısını kontrol et"
    fi
fi

# MouseJack bağımlılıkları
if [ -f "/opt/blackpony/mousejack/requirements.txt" ]; then
    info "MouseJack bağımlılıkları kuruluyor..."
    "$ENV_PATH/bin/pip" install -r /opt/blackpony/mousejack/requirements.txt 2>&1 | tail -3
    ok "MouseJack bağımlılıkları tamam"
fi

# Test
if "$ENV_PATH/bin/python3" /opt/blackpony/mousejack/mousejack.py --help &>/dev/null; then
    ok "MouseJack çalışıyor"
else
    warn "MouseJack --help yanıt vermedi (normal olabilir, RF24 gerekebilir)"
fi
echo ""

# ─────────────────────────────────────
# 3. nRF Research Firmware
# ─────────────────────────────────────
echo -e "${WHITE}  [3/5] nRF RESEARCH FIRMWARE${NC}"; sep

if [ -d "/opt/blackpony/nrf-research-firmware" ]; then
    ok "nRF Research Firmware zaten mevcut"
else
    info "nRF Research Firmware indiriliyor..."
    cd /opt/blackpony
    git clone --depth=1 https://github.com/BastilleResearch/nrf-research-firmware 2>&1 | tail -2
    ok "nRF Research Firmware indirildi"
fi
echo ""

# ─────────────────────────────────────
# 4. Launcher güncelle
# ─────────────────────────────────────
echo -e "${WHITE}  [4/5] LAUNCHER GUNCELLE${NC}"; sep

cat > /usr/local/bin/blackpony << EOF
#!/bin/bash
source $ENV_PATH/bin/activate
python3 /opt/blackpony/blackpony/main.py
EOF
chmod +x /usr/local/bin/blackpony
ok "Launcher güncellendi → $ENV_PATH kullanıyor"

# Desktop kısayolu
cat > /home/koray/Desktop/BlackPony.sh << EOF
#!/bin/bash
source $ENV_PATH/bin/activate
python3 /opt/blackpony/blackpony/main.py
EOF
chmod +x /home/koray/Desktop/BlackPony.sh
chown koray:koray /home/koray/Desktop/BlackPony.sh
ok "Desktop kısayolu oluşturuldu"
echo ""

# ─────────────────────────────────────
# 5. Özet
# ─────────────────────────────────────
echo -e "${WHITE}  [5/5] DURUM OZETI${NC}"; sep

chk() {
    local label="$1"; local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        echo -e "  ${GREEN}[✓]${NC} $label"
    else
        echo -e "  ${RED}[✗]${NC} $label"
    fi
}

chk "venv ($ENV_PATH)"              "[ -d '$ENV_PATH' ]"
chk "pyrf24"                        "$ENV_PATH/bin/python3 -c 'import pyrf24'"
chk "spidev"                        "$ENV_PATH/bin/python3 -c 'import spidev'"
chk "PyQt5"                         "$ENV_PATH/bin/python3 -c 'import PyQt5'"
chk "MouseJack"                     "[ -f '/opt/blackpony/mousejack/mousejack.py' ]"
chk "nRF Research Firmware"         "[ -d '/opt/blackpony/nrf-research-firmware' ]"
chk "main.py"                       "[ -f '/opt/blackpony/blackpony/main.py' ]"
chk "SPI /dev/spidev0.0"            "ls /dev/spidev0.0"
chk "Bluetooth hci0"                "hciconfig 2>/dev/null | grep -q hci0"
chk "airmon-ng"                     "command -v airmon-ng"
chk "Launcher /usr/local/bin"       "[ -x '/usr/local/bin/blackpony' ]"
chk "Desktop kısayolu"              "[ -f '/home/koray/Desktop/BlackPony.sh' ]"

echo ""
echo -e "${CYAN}  ════════════════════════════════════════${NC}"
echo -e "${GREEN}  Başlatmak için:${NC}"
echo ""
echo -e "  ${WHITE}blackpony${NC}"
echo -e "  ${DIM}veya masaüstündeki BlackPony.sh${NC}"
echo ""
