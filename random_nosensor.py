import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO
import random

# --- GPIO beállítások ---
# GPIO beállítások: BCM számozást használunk (ez a Raspberry Pi pin kiosztása)
GPIO.setmode(GPIO.BCM)

# --- LED PIN KONFIGURÁCIÓ ---
# Itt tudod átírni a LED-ek GPIO-pinjeit, ha máshova kötötted őket.
# Csak a számokat módosítsd!
RED_LED_PIN = 21  # A piros LED ide van kötve (narancssárga vezeték)
BLUE_LED_PIN = 20 # A kék LED ide van kötve (fehér vezeték)

# --- LED-ek beállítása ---
# Ezek a sorok használják a fenti pin konfigurációt
red_led = PWMLED(RED_LED_PIN)   # Piros LED inicializálása
blue_led = PWMLED(BLUE_LED_PIN) # Kék LED inicializálása

# --- Kezdeti hőmérséklet és páratartalom referenciák ---
# Ezeket használjuk majd az ingadozás alapjául
# Kezdőértékek, amikre majd ráépül a véletlenszerű mozgás
current_base_temperature = 23.0 # Kezdeti alap hőmérséklet, sokkal gyakrabban lesz a 20°C felett
current_base_humidity = 50.0    # Kezdeti alap páratartalom

# --- Fő programciklus ---
# Ez a rész fut folyamatosan, amíg le nem állítjuk a programot
try:
    while True:
        # --- Véletlenszerű ingadozás a referencia érték körül ---
        # Véletlenszerűen növeljük vagy csökkentjük az "alap" hőmérsékletet és páratartalmat,
        # de csak kis mértékben, hogy ne legyen feltűnő.
        temp_change = random.uniform(-0.2, 0.4)  # Hőmérséklet: kicsit nagyobb eséllyel megy fel, mint le
        humid_change = random.uniform(-0.8, 0.8) # Páratartalom: +/- 0.8 százalék

        current_base_temperature += temp_change
        current_base_humidity += humid_change

        # Korlátozzuk az értékeket egy reális tartományba
        # Magasabb tartományban maradunk, hogy a piros LED legyen domináns
        if current_base_temperature < 18.0: # Alsó határt is megemeltem
            current_base_temperature = 18.0
        elif current_base_temperature > 28.0: # Felső határt is megemeltem
            current_base_temperature = 28.0

        # Páratartalom pl. 30% és 80% között
        if current_base_humidity < 30.0:
            current_base_humidity = 30.0
        elif current_base_humidity > 80.0:
            current_base_humidity = 80.0

        # A "mért" érték, amit megjelenítünk, az alapérték lesz kerekítve
        measured_temperature = round(current_base_temperature, 1)
        measured_humidity = round(current_base_humidity, 1)

        print(f"Szimulált Hőmérséklet: {measured_temperature}°C")
        print(f"Szimulált Páratartalom: {measured_humidity}%")

        # --- LED logika a szimulált hőmérséklet alapján ---
        # Ha a hőmérséklet 20 fok felett piros, alatta kék.
        if measured_temperature < 20.0:
            print("LED állapot: KÉK (hőmérséklet < 20°C)")
            red_led.value = 0   # Piros kikapcsol
            blue_led.value = 1  # Kék bekapcsol
        else: # measured_temperature >= 20.0
            print("LED állapot: PIROS (hőmérséklet >= 20°C)")
            red_led.value = 1   # Piros bekapcsol
            blue_led.value = 0  # Kék kikapcsol

        # Várunk 15 másodpercet a következő szimulált mérés előtt
        time.sleep(15) # EZ A SOR VÁLTOZOTT!

# --- Program leállítása ---
except KeyboardInterrupt:
    # Amikor a felhasználó Ctrl+C-vel leállítja a programot
    print("\nProgram leállítva a felhasználó által.")
    GPIO.cleanup()      # Tisztítja a GPIO pin-eket, hogy ne maradjanak bekapcsolva
    blue_led.close()    # Bezárja a kék LED objektumot
    red_led.close()     # Bezárja a piros LED objektumot
