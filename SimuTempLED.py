import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO
import random

# --- GPIO beállítások ---
# Beállítja a GPIO lábak számozási módját BCM (Broadcom) szerint.
GPIO.setmode(GPIO.BCM)

# --- LED-ek beállítása ---
# Létrehozza a PWMLED objektumokat a piros és kék LED-ekhez a megadott GPIO pineken.
# A PWMLED lehetővé teszi a fényerő szabályozását is, bár itt csak ki/be kapcsolás történik.
red_led = PWMLED(21)    # Piros LED a GPIO 21-es pin-en
blue_led = PWMLED(20)   # Kék LED a GPIO 20-as pin-en

# --- Kezdeti értékek ---
# A hőmérséklet és páratartalom szimulált kezdeti értékei.
current_temperature = 18.0
current_humidity = 60.0

try:
    print("Program indult. A hőmérséklet és páratartalom szimulálva lesz, és a LED-ek ennek alapján fognak váltani.")

    # 3 kezdeti ciklus: fix értékekkel, biztosan a hideg (kék LED) állapotot mutatja be.
    # Ez segít a demó indításánál, hogy a felhasználó lássa a kiinduló állapotot.
    for i in range(3):
        if current_temperature > 20: # Ha az aktuális hőmérséklet nagyobb mint 20
            red_led.value = 1        # Akkor a piros LED világít
            blue_led.value = 0       # A kék LED ki van kapcsolva
        else:                        # Ha az aktuális hőmérséklet 20 vagy alatta van
            red_led.value = 0        # Akkor a piros LED ki van kapcsolva
            blue_led.value = 1       # A kék LED világít

        print(f"Kezdő állapot ({i+1}/3): Hőmérséklet: {current_temperature:.1f}°C, Páratartalom: {current_humidity:.1f}%")
        time.sleep(5) # Várakozás 5 másodpercet

    # Fő ciklus – a szimulált értékek lassan változnak.
    while True:
        # --- Hőmérséklet változás szimulálása ---
        # Ha a hőmérséklet 26°C alatt van, növeli azt véletlenszerűen.
        if current_temperature < 26.0:
            current_temperature += random.uniform(0.3, 0.7)
        else:
            # Ha túl meleg lenne (26°C felett), csak kicsit ingadozzon a hőmérséklet.
            current_temperature += random.uniform(-0.2, 0.2)

        # --- Páratartalom változás szimulálása ---
        # Véletlenszerűen változtatja a páratartalmat.
        current_humidity += random.uniform(-0.5, 0.5)
        # Biztosítja, hogy a páratartalom 0 és 100% között maradjon.
        current_humidity = max(0, min(100, current_humidity))

        # --- LED logika ---
        # A LED-ek állapotának frissítése a szimulált hőmérséklet alapján.
        if current_temperature > 20: # Ha a hőmérséklet meghaladja a 20°C-ot
            red_led.value = 1        # Piros LED be
            blue_led.value = 0       # Kék LED ki
        else:                        # Ha a hőmérséklet 20°C vagy alatta van
            red_led.value = 0        # Piros LED ki
            blue_led.value = 1       # Kék LED be

        # --- Kiírás konzolra ---
        print(f"Hőmérséklet: {current_temperature:.1f}°C, Páratartalom: {current_humidity:.1f}%")
        print(f"Aktív LED: {'Piros' if current_temperature > 20 else 'Kék'}")

        time.sleep(5) # Várakozás 5 másodpercet a következő szimulációig

except KeyboardInterrupt:
    # Program leállítása CTRL+C billentyűkombinációval.
    print("\nProgram leállítva a felhasználó által.")
    # A GPIO lábak felszabadítása a tiszta kilépés érdekében.
    GPIO.cleanup()
    # A LED objektumok bezárása.
    blue_led.close()
    red_led.close()
