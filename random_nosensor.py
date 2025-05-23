import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO
import random

# --- GPIO beállítások ---
# GPIO beállítások: BCM számozást használunk (ez a Raspberry Pi pin kiosztása)
GPIO.setmode(GPIO.BCM)

# --- LED-ek beállítása ---
# Piros LED (narancssárga vezeték) -> GPIO 21
# Kék LED (fehér vezeték) -> GPIO 20
red_led = PWMLED(21)    # Piros LED a GPIO 21-es pin-en
blue_led = PWMLED(20)   # Kék LED a GPIO 20-as pin-en

# --- Kezdeti értékek beállítása ---
# Kezdő hőmérséklet alacsonyabb, hogy kék legyen a LED az elején (20 fok alatt)
current_temperature = 18.0
# Kezdeti páratartalom érték
current_humidity = 60.0

# --- Fő programciklus ---
try:
    print("Program indult. A hőmérséklet és páratartalom szimulálva lesz, és a LED-ek ennek alapján fognak váltani.")

    # Kezdetben 3 ciklusban biztosan kék a LED (mivel a hőmérséklet 20 fok alatt van)
    for i in range(3):
        # LED logika az aktuális hőmérséklet alapján
        if current_temperature > 20: # 20 fok felett -> PIROS LED
            red_led.value = 1
            blue_led.value = 0
        else: # 20 fok vagy alatta -> KÉK LED
            red_led.value = 0
            blue_led.value = 1

        # Kiírjuk a kezdeti szimulált adatokat
        print(f"Kezdő állapot ({i+1}/3): Hőmérséklet: {current_temperature:.1f}°C, Páratartalom: {current_humidity:.1f}%")
        time.sleep(5) # Vár 5 másodpercet

    # Lassan növeljük a hőmérsékletet, amíg 20 fölé nem emelkedik
    while True:
        # --- Szimulált adatok generálása és lassú változtatása ---
        # Növeljük a hőmérsékletet kis lépésekben (pl. +0.3 és +0.7 fok/ciklus)
        current_temperature += random.uniform(0.3, 0.7)
        # Páratartalmat is kicsit változtatjuk, de lassabban
        current_humidity += random.uniform(-1.0, 1.0) # +/- 1.0% változás
        
        # Biztosítjuk, hogy a páratartalom reális tartományban maradjon (0-100%)
        if current_humidity < 0:
            current_humidity = 0
        elif current_humidity > 100:
            current_humidity = 100

        # --- LED logika: 20 fok FELETT PIROS, ALATT KÉK ---
        if current_temperature > 20: # Ha a hőmérséklet 20 fok FÖLÖTT van
            red_led.value = 1   # Piros LED bekapcsol (teljes fényerő)
            blue_led.value = 0  # Kék LED kikapcsol
        else: # Ha a hőmérséklet 20 fok vagy ALATTA van
            red_led.value = 0   # Piros LED kikapcsol
            blue_led.value = 1  # Kék LED bekapcsol (teljes fényerő)

        # Kiírjuk az aktuális szimulált értékeket
        print(f"Hőmérséklet: {current_temperature:.1f}°C, Páratartalom: {current_humidity:.1f}%")
        print(f"Aktív LED: {'Piros' if current_temperature > 20 else 'Kék'}") # Ezt a sort vizsgán akár ki is lehet kommentelni

        # Ha a hőmérséklet túl magas lett, visszaállítjuk egy alacsonyabb értékre
        if current_temperature > 25.0: # Ha elérte a 25 fokot, visszaállítjuk
            print("\nHőmérséklet túl magas, visszaállítás egy alacsonyabb értékre.\n")
            current_temperature = random.uniform(15.0, 19.0) # Visszaáll egy random alacsony értékre
            # A páratartalmat is visszaállíthatjuk egy középértékre, vagy hagyhatjuk ahol van
            current_humidity = random.uniform(50.0, 70.0)
            time.sleep(3) # Kis szünet az újraindítás előtt

        time.sleep(5) # Vár 5 másodpercet a következő frissítés előtt

# --- Program leállítása ---
except KeyboardInterrupt:
    # Amikor a felhasználó Ctrl+C-vel leállítja a programot
    print("\nProgram leállítva a felhasználó által.")
    GPIO.cleanup()      # Tisztítja a GPIO pin-eket
    blue_led.close()    # Bezárja a kék LED objektumot
    red_led.close()     # Bezárja a piros LED objektumot
  
