from machine import I2C, Pin
import time
from vl53l4cd import VL53L4CD

# 1. I2C Initialisierung (Pico 2 XL W)
# Pins: SDA=GP4, SCL=GP5
i2c0 = I2C(0, sda=Pin(4), scl=Pin(5), freq=200000)

print("Initialisiere Sensor...")
sensor0 = VL53L4CD(i2c0)

# 2. Sensor-Konfiguration für High-Speed (100Hz Ziel)
# Wir setzen das Timing-Budget auf 10ms für schnellere Messzyklen
#sensor0.inter_measurement = 20 
#sensor0.timing_budget = 50 

# Startet den Messmodus
sensor0.start_ranging()

print("Messung läuft. Zeitstempel startet bei 0ms.")
print("Drücke Strg+C zum Stoppen.")
print("-" * 20)
print("time_ms;distance_mm") # Header für CSV

# Referenzzeitpunkt für den Nullpunkt setzen
start_time = time.ticks_ms()

try:
    while True:
        # Aktuelle Zeit holen und Differenz zum Start berechnen
        now = time.ticks_ms()
        timestamp_zero = time.ticks_diff(now, start_time)
        
        # Distanzwert auslesen
        dist = sensor0.read()
        
        if dist != -1:
            # Ausgabe: Zeitstempel startet bei 0, danach Distanz
            print("{};{}".format(timestamp_zero, dist))
        
        # Kurze Pause, um den Bus nicht zu überlasten 
        # Da sensor0.read() blockiert, bis ein Wert da ist, 
        # regelt sich die Frequenz hier fast von selbst.
        time.sleep_ms(8)

except KeyboardInterrupt:
    print("\nMessung beendet.")
    sensor0.stop_ranging()