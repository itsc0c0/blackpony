#!/bin/bash

# ╔══════════════════════════════════════════╗
# ║     BLACK PONY — RF24 ULTIMATE FIX      ║
# ║     Her yöntemi sırayla dener           ║
# ╚══════════════════════════════════════════╝

GREEN='\033[0;32m'; RED='\033[0;31m'
YELLOW='\033[1;33m'; CYAN='\033[0;36m'
WHITE='\033[1;37m'; DIM='\033[0;90m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}[✓]${NC} $1"; }
err()  { echo -e "  ${RED}[✗]${NC} $1"; }
info() { echo -e "  ${CYAN}[*]${NC} $1"; }
warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }
sep()  { echo -e "  ${DIM}────────────────────────────────────────${NC}"; }
head() { echo -e "\n  ${WHITE}$1${NC}"; sep; }

clear
echo -e "${WHITE}"
echo "  ██████  ███████ ██████   ██  ██  "
echo "  ██   ██ ██      ╚════██  ██  ██  "
echo "  ██████  █████    █████   ██████  "
echo "  ██   ██ ██      ██       ╚═══██  "
echo "  ██   ██ ██      ███████      ██  "
echo -e "${NC}"
echo -e "${CYAN}  ════════════════════════════════════════${NC}"
echo -e "${YELLOW}       RF24 ULTIMATE INSTALLER           ${NC}"
echo -e "${CYAN}  ════════════════════════════════════════${NC}"
echo ""

# Root kontrolü
if [ "$EUID" -ne 0 ]; then
    err "Root gerekli: sudo bash rf24_ultimate.sh"
    exit 1
fi

# Kullanıcı home dizini bul
REAL_USER=$(logname 2>/dev/null || echo "pi")
USER_HOME=$(eval echo "~$REAL_USER")
ok "Kullanıcı: $REAL_USER | Home: $USER_HOME"

# RF24 kurulu mu kontrol fonksiyonu
check_rf24() {
    python3 -c "import RF24" 2>/dev/null
    return $?
}

# Zaten kurulu mu?
if check_rf24; then
    ok "RF24 zaten kurulu!"
    python3 -c "import RF24; print('  Versiyon:', RF24.__version__ if hasattr(RF24,'__version__') else 'OK')"
    exit 0
fi

warn "RF24 kurulu değil — tüm yöntemler deneniyor..."
echo ""

# Bağımlılıklar
head "[0] BAGIMLILIKLARI HAZIRLA"
apt update -qq 2>/dev/null
apt install -y -qq \
    git cmake python3-dev python3-pip python3-venv python3-setuptools \
    libboost-python-dev libboost-dev build-essential \
    python3-spidev python3-rpi.gpio 2>/dev/null
ok "Bağımlılıklar hazır"

# ─────────────────────────────────────────────
# YÖNTEM 1: Direkt pip
# ─────────────────────────────────────────────
head "[1/7] DIREKT PIP"
info "pip3 install pyrf24 deneniyor..."
cd "$USER_HOME"
python3 -m pip install pyrf24 --break-system-packages --no-cache-dir 2>&1 | tail -3
if check_rf24; then ok "YÖNTEM 1 BAŞARILI!"; exit 0
else err "Yöntem 1 başarısız"; fi

# ─────────────────────────────────────────────
# YÖNTEM 2: pip --user
# ─────────────────────────────────────────────
head "[2/7] PIP --user"
info "pip3 install pyrf24 --user deneniyor..."
cd "$USER_HOME"
sudo -u "$REAL_USER" python3 -m pip install pyrf24 --user --no-cache-dir 2>&1 | tail -3
if check_rf24; then ok "YÖNTEM 2 BAŞARILI!"; exit 0
else err "Yöntem 2 başarısız"; fi

# ─────────────────────────────────────────────
# YÖNTEM 3: Virtualenv
# ─────────────────────────────────────────────
head "[3/7] VIRTUALENV"
info "Virtual environment oluşturuluyor..."
cd "$USER_HOME"
sudo -u "$REAL_USER" python3 -m venv "$USER_HOME/bp_env" --system-site-packages 2>/dev/null
source "$USER_HOME/bp_env/bin/activate"
pip install pyrf24 --no-cache-dir 2>&1 | tail -3
if python3 -c "import RF24" 2>/dev/null; then
    ok "YÖNTEM 3 BAŞARILI — virtualenv içinde!"
    # Launcher'ı güncelle
    cat > /usr/local/bin/blackpony << EOF
#!/bin/bash
source $USER_HOME/bp_env/bin/activate
python3 /opt/blackpony/blackpony/main.py
EOF
    chmod +x /usr/local/bin/blackpony
    ok "Launcher güncellendi (venv kullanıyor)"
    deactivate
    exit 0
else
    err "Yöntem 3 başarısız"
    deactivate 2>/dev/null
fi

# ─────────────────────────────────────────────
# YÖNTEM 4: Wheel dosyası ile
# ─────────────────────────────────────────────
head "[4/7] WHEEL DOSYASI"
info "Wheel indiriliyor..."
cd "$USER_HOME"
rm -rf rf24_wheel && mkdir rf24_wheel && cd rf24_wheel
python3 -m pip download pyrf24 --no-deps 2>&1 | tail -3
WHL=$(ls *.whl 2>/dev/null | head -1)
if [ -n "$WHL" ]; then
    info "Wheel bulundu: $WHL — kuruluyor..."
    python3 -m pip install "$WHL" --break-system-packages 2>&1 | tail -3
    if check_rf24; then ok "YÖNTEM 4 BAŞARILI!"; cd "$USER_HOME"; exit 0
    else err "Yöntem 4 başarısız"; fi
else
    err "Wheel indirilemedi"
fi
cd "$USER_HOME"

# ─────────────────────────────────────────────
# YÖNTEM 5: GitHub kaynak — RF24 C++ + pyRF24
# ─────────────────────────────────────────────
head "[5/7] GITHUB KAYNAK DERLEME"
info "RF24 C++ kütüphanesi derleniyor..."
cd "$USER_HOME"
rm -rf rf24_src && mkdir rf24_src && cd rf24_src

# RF24 C++ lib
git clone --depth=1 https://github.com/nRF24/RF24.git 2>&1 | tail -2
cd RF24
cmake . -DCMAKE_BUILD_TYPE=Release -Wno-dev > /dev/null 2>&1
make -j4 2>&1 | tail -2
make install 2>/dev/null
ldconfig
ok "RF24 C++ lib derlendi"

# pyRF24
cd "$USER_HOME/rf24_src"
git clone --depth=1 https://github.com/nRF24/pyRF24.git 2>&1 | tail -2
cd pyRF24
python3 -m pip install . --break-system-packages 2>&1 | tail -3
if check_rf24; then
    ok "YÖNTEM 5 BAŞARILI!"
    cd "$USER_HOME"; exit 0
else
    err "Yöntem 5 başarısız"
fi
cd "$USER_HOME"

# ─────────────────────────────────────────────
# YÖNTEM 6: RF24 eski sürüm dene
# ─────────────────────────────────────────────
head "[6/7] ESKI SURUM"
info "pyrf24==1.4.0 deneniyor..."
cd "$USER_HOME"
python3 -m pip install pyrf24==1.4.0 --break-system-packages --no-cache-dir 2>&1 | tail -3
if check_rf24; then ok "YÖNTEM 6 BAŞARILI!"; exit 0; fi

info "pyrf24==1.3.0 deneniyor..."
python3 -m pip install pyrf24==1.3.0 --break-system-packages --no-cache-dir 2>&1 | tail -3
if check_rf24; then ok "YÖNTEM 6 BAŞARILI!"; exit 0
else err "Yöntem 6 başarısız"; fi

# ─────────────────────────────────────────────
# YÖNTEM 7: Manuel .so kopyalama
# ─────────────────────────────────────────────
head "[7/7] MANUEL .so ARAMA"
info "Derlenmiş RF24 dosyaları aranıyor..."
SO_FILE=$(find "$USER_HOME" /tmp /usr /opt -name "RF24*.so" 2>/dev/null | head -1)
PY_FILE=$(find "$USER_HOME" /tmp /usr /opt -name "RF24.py" 2>/dev/null | head -1)

SITE_PKG=$(python3 -c "import site; print(site.getsitepackages()[0])" 2>/dev/null)
info "Site packages: $SITE_PKG"

if [ -n "$SO_FILE" ]; then
    info ".so bulundu: $SO_FILE"
    cp "$SO_FILE" "$SITE_PKG/" 2>/dev/null
    [ -n "$PY_FILE" ] && cp "$PY_FILE" "$SITE_PKG/" 2>/dev/null
    if check_rf24; then ok "YÖNTEM 7 BAŞARILI!"; exit 0
    else err ".so kopyalandı ama import hâlâ olmadı"; fi
else
    err ".so dosyası bulunamadı"
fi

# ─────────────────────────────────────────────
# HİÇBİRİ ÇALIŞMADI
# ─────────────────────────────────────────────
echo ""
echo -e "${CYAN}  ════════════════════════════════════════${NC}"
err "RF24 hiçbir yöntemle kurulamadı."
echo ""
warn "Tam hata için:"
echo -e "  ${WHITE}python3 -m pip install pyrf24 --break-system-packages -v 2>&1 | tail -30${NC}"
echo ""
warn "Alternatif: RF24 olmadan spidev ile sweep çalışıyor."
warn "SCAN/ATTACK için MouseJack zaten RF24 gerektiriyor."
echo ""
echo -e "${CYAN}  ════════════════════════════════════════${NC}"
