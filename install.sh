#!/bin/bash

# ╔══════════════════════════════════════╗
# ║      BLACK PONY — INSTALLER          ║
# ║      nRF24 Pentest Toolkit           ║
# ╚══════════════════════════════════════╝

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

clear
echo -e "${CYAN}"
echo "  ██████  ██████  ██      █████   ██████ ██   ██     ██████   ██████  ███    ██ ██    ██"
echo "  ██   ██ ██   ██ ██     ██   ██ ██      ██  ██      ██   ██ ██    ██ ████   ██  ██  ██ "
echo "  ██████  ██████  ██     ███████ ██      █████       ██████  ██    ██ ██ ██  ██   ████  "
echo "  ██   ██ ██   ██ ██     ██   ██ ██      ██  ██      ██      ██    ██ ██  ██ ██    ██   "
echo "  ██████  ██████  ██████ ██   ██  ██████ ██   ██     ██       ██████  ██   ████    ██   "
echo -e "${NC}"
echo -e "${WHITE}  ════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}              INSTALLER v1.0 — nRF24 Module${NC}"
echo -e "${WHITE}  ════════════════════════════════════════════════════${NC}"
echo ""

log_ok()   { echo -e "  ${GREEN}[✓]${NC} $1"; }
log_err()  { echo -e "  ${RED}[✗]${NC} $1"; }
log_info() { echo -e "  ${CYAN}[*]${NC} $1"; }
log_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }

# ── Root kontrolü ──────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
  log_err "Root gerekli. Tekrar çalıştır: sudo bash install.sh"
  exit 1
fi
log_ok "Root yetkisi confirmed"

# ── Sistem güncellemesi ────────────────────────────────────
echo ""
echo -e "${CYAN}  [1/6] Sistem güncelleniyor...${NC}"
apt update -qq && apt upgrade -y -qq
log_ok "Sistem güncellendi"

# ── Sistem bağımlılıkları ──────────────────────────────────
echo ""
echo -e "${CYAN}  [2/6] Sistem paketleri kuruluyor...${NC}"
apt install -y -qq \
    python3 \
    python3-pip \
    python3-pyqt5 \
    python3-dev \
    python3-rpi.gpio \
    git \
    cmake \
    build-essential \
    libboost-all-dev \
    libglib2.0-dev \
    i2c-tools \
    pigpio \
    python3-pigpio

log_ok "Sistem paketleri kuruldu"

# ── SPI Aktif et ───────────────────────────────────────────
echo ""
echo -e "${CYAN}  [3/6] SPI & GPIO yapılandırılıyor...${NC}"

# SPI kernel modülü
if ! lsmod | grep -q spi_bcm2835; then
    modprobe spi_bcm2835
fi

# config.txt SPI satırı
CONFIG="/boot/firmware/config.txt"
[ ! -f "$CONFIG" ] && CONFIG="/boot/config.txt"

if ! grep -q "dtparam=spi=on" "$CONFIG"; then
    echo "dtparam=spi=on" >> "$CONFIG"
    log_ok "SPI config.txt'e eklendi"
else
    log_ok "SPI zaten aktif (config.txt)"
fi

# /dev/spidev kontrol
if ls /dev/spidev* &>/dev/null; then
    log_ok "SPI cihazı bulundu: $(ls /dev/spidev*)"
else
    log_warn "SPI cihazı şu an görünmüyor — reboot sonrası aktif olacak"
fi

# ── Python kütüphaneleri ───────────────────────────────────
echo ""
echo -e "${CYAN}  [4/6] Python kütüphaneleri kuruluyor...${NC}"

pip3 install --break-system-packages --quiet \
    pyrf24 \
    RPi.GPIO \
    spidev \
    pyserial 2>/dev/null || \
pip3 install --quiet \
    pyrf24 \
    RPi.GPIO \
    spidev \
    pyserial

log_ok "Python kütüphaneleri kuruldu"

# RF24 C++ kütüphanesi (daha stabil)
log_info "RF24 C++ kütüphanesi kuruluyor..."
if [ ! -d "/tmp/RF24" ]; then
    git clone --depth=1 https://github.com/nRF24/RF24.git /tmp/RF24 -q
fi
cd /tmp/RF24
cmake . -DCMAKE_BUILD_TYPE=Release -Wno-dev > /dev/null 2>&1
make -j4 > /dev/null 2>&1
make install > /dev/null 2>&1
ldconfig
log_ok "RF24 C++ kuruldu"

# ── MouseJack araçları ─────────────────────────────────────
echo ""
echo -e "${CYAN}  [5/6] MouseJack araçları indiriliyor...${NC}"

INSTALL_DIR="/opt/blackpony"
mkdir -p "$INSTALL_DIR"

if [ ! -d "$INSTALL_DIR/mousejack" ]; then
    git clone --depth=1 https://github.com/BastilleResearch/mousejack "$INSTALL_DIR/mousejack" -q
    log_ok "MouseJack indirildi → $INSTALL_DIR/mousejack"
else
    log_ok "MouseJack zaten mevcut"
fi

if [ ! -d "$INSTALL_DIR/nrf-research-firmware" ]; then
    git clone --depth=1 https://github.com/BastilleResearch/nrf-research-firmware "$INSTALL_DIR/nrf-research-firmware" -q
    log_ok "nRF Research Firmware indirildi"
else
    log_ok "nRF Research Firmware zaten mevcut"
fi

# ── Black Pony klasörü ─────────────────────────────────────
echo ""
echo -e "${CYAN}  [6/6] Black Pony klasörü hazırlanıyor...${NC}"

mkdir -p "$INSTALL_DIR/blackpony"
mkdir -p "$INSTALL_DIR/blackpony/modules"
mkdir -p "$INSTALL_DIR/blackpony/logs"
mkdir -p "$INSTALL_DIR/blackpony/assets"

# Launcher script
cat > /usr/local/bin/blackpony << 'EOF'
#!/bin/bash
cd /opt/blackpony/blackpony
python3 main.py
EOF
chmod +x /usr/local/bin/blackpony

log_ok "Launcher oluşturuldu → 'blackpony' komutuyla başlatılabilir"

# ── Sonuç ──────────────────────────────────────────────────
echo ""
echo -e "${WHITE}  ════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  [✓] KURULUM TAMAMLANDI${NC}"
echo -e "${WHITE}  ════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYAN}Kurulum dizini :${NC} $INSTALL_DIR"
echo -e "  ${CYAN}SPI cihazı     :${NC} $(ls /dev/spidev* 2>/dev/null || echo 'Reboot gerekli')"
echo ""
echo -e "  ${YELLOW}[!] Eğer SPI görünmüyorsa reboot yap:${NC}"
echo -e "      ${WHITE}sudo reboot${NC}"
echo ""
echo -e "  ${GREEN}Black Pony GUI hazır olunca başlatmak için:${NC}"
echo -e "      ${WHITE}blackpony${NC}"
echo ""
echo -e "${CYAN}  ██████  ██████  ███    ██ ██    ██ ${NC}"
echo -e "${CYAN}  ██   ██ ██   ██ ████   ██  ██  ██  ${NC}"
echo -e "${CYAN}  ██████  ██████  ██ ██  ██   ████   ${NC}"
echo -e "${CYAN}  ██      ██      ██  ██ ██    ██    ${NC}"
echo -e "${CYAN}  ██      ██      ██   ████    ██    ${NC}"
echo ""
