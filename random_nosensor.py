import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO
import random

# --- GPIO beállítások ---
# GPIO beállítások: BCM számozást használunk
GPIO.setmode(GPIO.BCM)

# --- LED-ek beállítása ---
# Piros LED (narancssárga vezeték) -> GPIO 21
# Kék LED (fehér vezeték) -> GPIO 20
red_led = PWMLED(21)    # Piros LED a GPIO 21-es pin-en
blue_led = PWMLED(20)   # Kék LED a GPIO 20-as pin-en

# --- Kezdeti értékek beállítása ---
# Kezdő hőmérséklet alacsonyabb, hogy kék legyen a LED az elején
current_temperature = 18.0 # Kezdeti hőmérséklet (pl. 18 fok)
simulated_humidity = 60.0  # Szimulált páratartalom

# --- Fő programciklus ---
try:
    print("Program indult. Figyeld a LED-ek változását!")

    # Kezdetben 3 ciklusban biztosan kék a LED (vagy amilyen a current_temperature alapján kellene lennie)
    for i in range(3):
        # A LED logika itt csak az inicializált current_temperature alapján kapcsol
        if current_temperature > 20: # 20 fok felett -> PIROS
            red_led.value = 1
            blue_led.value = 0
        else: # 20 fok vagy alatta -> KÉK
            red_led.value = 0
            blue_led.value = 1

        print(f"Ciklus {i+1}: Hőmérséklet: {current_temperature:.1f}°C")
        time.sleep(5) # Vár 5 másodpercet

    # Lassan növeljük a hőmérsékletet, amíg 20 fölé nem emelkedik
    while True:
        # Növeljük a hőmérsékletet kis lépésekben (pl. +0.3 és +0.7 fok/ciklus)
        current_temperature += random.uniform(0.3, 0.7)

        # Páratartalmat is kicsit változtatjuk
        simulated_humidity += random.uniform(-1.0, 1.0)
        if simulated_humidity < 0: simulated_humidity = 0
        if simulated_humidity > 100: simulated_humidity = 100

        # --- LED logika: 20 fok FELETT PIROS, ALATT KÉK ---
        if current_temperature > 20: # Ha a hőmérséklet 20 fok FÖLÖTT van
            red_led.value = 1   # Piros LED bekapcsol (teljes fényerő)
            blue_led.value = 0  # Kék LED kikapcsol
        else: # Ha a hőmérséklet 20 fok vagy ALATTA van
            red_led.value = 0   # Piros LED kikapcsol
            blue_led.value = 1  # Kék LED bekapcsol (teljes fényerő)

        # DEBUG: Csak akkor írjuk ki az értékeket, ha látni akarjuk a változást
        print(f"Hőmérséklet: {current_temperature:.1f}°C. Aktív LED: {'Piros' if current_temperature > 20 else 'Kék'}")

        # Ha a hőmérséklet túl magas lett, visszaállítjuk egy alacsonyabb értékre, hogy újra kék legyen
        if current_temperature > 25.0: # Ha elérte a 25 fokot, visszaállítjuk
            print("\nHőmérséklet túl magas, visszaállítás egy alacsonyabb értékre.\n")
            current_temperature = random.uniform(15.0, 19.0) # Visszaáll egy random alacsony értékre
            time.sleep(3) # Kis szünet az újraindítás előtt

        time.sleep(5) # Vár 5 másodpercet a következő frissítés előtt

except KeyboardInterrupt:
    print("\nProgram leállítva a felhasználó által.")
    GPIO.cleanup()
    blue_led.close()
    red_led.close()

    
