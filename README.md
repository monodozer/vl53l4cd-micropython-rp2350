# vl53l4cd-micropython-rp2350
i build a vl53l4cd distancesensor liblrary for micropython.

library is vl53l4cd.py
and a check test.py

you can change internal mesurment and timing budget in vl53l4cd.py

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
