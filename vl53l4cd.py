import time
import struct
from machine import I2C, Pin

class VL53L4CD:
    def __init__(self, i2c, address=0x29):
        self._i2c = i2c
        self._address = address
        
        # 1. Boot & ID Check
        try:
            if self._read_reg(0x010F, 2) != b'\xeb\xaa':
                raise RuntimeError("Sensor ID falsch")
        except:
            raise RuntimeError("Sensor nicht gefunden")
        
        # Warten auf Boot (Status 0x03)
        while self._read_reg(0x00E5)[0] != 0x03:
            time.sleep_ms(1)

        # 2. Adafruit / ST Standard-Initialisierung (90 Bytes)
        init_seq = b"\x12\x00\x00\x11\x02\x00\x02\x08\x00\x08\x10\x01\x01\x00\x00\x00\x00\xff\x00\x0f\x00\x00\x00\x00\x00\x20\x0b\x00\x00\x02\x14\x21\x00\x00\x05\x00\x00\x00\x00\xc8\x00\x00\x38\xff\x01\x00\x08\x00\x00\x01\xcc\x07\x01\xf1\x05\x00\xa0\x00\x80\x08\x38\x00\x00\x00\x00\x0f\x89\x00\x00\x00\x00\x00\x00\x00\x01\x07\x05\x06\x06\x00\x00\x02\xc7\xff\x9b\x00\x00\x00\x01\x00\x00"
        self._write_reg(0x002D, init_seq)

        # 3. VHV Start (Kalibrierung der Laser-Spannung)
        # Wir starten kurz, warten auf ein Signal und stoppen wieder
        self._write_reg(0x0087, b"\x21") 
        start_cal = time.ticks_ms()
        while (self._read_reg(0x0031)[0] & 0x01) != 0: # Warten auf Data Ready (Polarität beachten)
            if time.ticks_diff(time.ticks_ms(), start_cal) > 500:
                break # Timeout Schutz
            time.sleep_ms(1)
        
        self.clear_interrupt()
        self.stop_ranging()

        # 4. HIGH SPEED SETUP (100Hz / 10ms)
        
        # Timing Budget: 8ms (vorkalkulierte Registerwerte für 100Hz)
        self._write_reg(0x005E, b"\x04\x04") # RANGE_CONFIG_A (etwas kürzer)
        self._write_reg(0x0061, b"\x03\x08") # RANGE_CONFIG_B (etwas kürzer)
        
        #timing budget: 10ms
        
        #self._write_reg(0x005E, b"\x05\x04") # RANGE_CONFIG_A
        #self._write_reg(0x0061, b"\x03\x08") # RANGE_CONFIG_B
        
        # Inter-Measurement: 0ms (Erzwingt Continuous Mode)
        self._write_reg(0x006C, b"\x00\x00\x00\x00")
        
        # Zusätzliche VHV-Stabilisierung (aus Adafruit Lib)
        self._write_reg(0x0008, b"\x09")
        self._write_reg(0x000B, b"\x00")
        self._write_reg(0x0024, b"\x05\x00")

        # 5. FINALER START
        self.start_ranging()

    def _write_reg(self, reg, data):
        self._i2c.writeto_mem(self._address, reg, data, addrsize=16)

    def _read_reg(self, reg, n=1):
        return self._i2c.readfrom_mem(self._address, reg, n, addrsize=16)

    def start_ranging(self):
        self._write_reg(0x0087, b"\x21")

    def stop_ranging(self):
        self._write_reg(0x0087, b"\x00")

    def clear_interrupt(self):
        self._write_reg(0x0086, b"\x01")

    def data_ready(self):
        # WICHTIG: Die Polarität im Register 0x0031 (Bit 0) 
        # 0 bedeutet hier: Daten sind da (nach der Standard-Init)
        return (self._read_reg(0x0031)[0] & 0x01) == 0

    def read(self):
        """Liest Distanz in mm. Liefert -1 wenn keine neuen Daten."""
        if self.data_ready():
            data = self._read_reg(0x0096, 2)
            dist = struct.unpack(">H", data)[0]
            self.clear_interrupt()
            return dist
        return -1