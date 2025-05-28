import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO
import random

# --- GPIO beállítások ---
GPIO.setmode(GPIO.BCM)

# --- LED-ek beállítása ---
red_led = PWMLED(21)    # Piros LED a GPIO 21-es pin-en
blue_led = PWMLED(20)   # Kék LED a GPIO 20-as pin-en

# --- Kezdeti értékek ---
current_temperature = 18.0
current_humidity = 60.0

try:
    print("Program indult. A hőmérséklet és páratartalom szimulálva lesz, és a LED-ek ennek alapján fognak váltani.")

    # 3 kezdeti ciklus: fix értékekkel, biztosan kék LED
    for i in range(3):
        if current_temperature > 20:
            red_led.value = 1
            blue_led.value = 0
        else:
            red_led.value = 0
            blue_led.value = 1

        print(f"Kezdő állapot ({i+1}/3): Hőmérséklet: {current_temperature:.1f}°C, Páratartalom: {current_humidity:.1f}%")
        time.sleep(5)

    # Fő ciklus – szimulált értékek lassan változnak
    while True:
        # --- Hőmérséklet változás ---
        if current_temperature < 26.0:
            current_temperature += random.uniform(0.3, 0.7)
        else:
            # Ha túl meleg lenne, csak kicsit ingadozzon
            current_temperature += random.uniform(-0.2, 0.2)

        # --- Páratartalom változás ---
        current_humidity += random.uniform(-0.5, 0.5)
        current_humidity = max(0, min(100, current_humidity))  # 0-100% között maradjon

        # --- LED logika ---
        if current_temperature > 20:
            red_led.value = 1
            blue_led.value = 0
        else:
            red_led.value = 0
            blue_led.value = 1

        # --- Kiírás konzolra ---
        print(f"Hőmérséklet: {current_temperature:.1f}°C, Páratartalom: {current_humidity:.1f}%")
        print(f"Aktív LED: {'Piros' if current_temperature > 20 else 'Kék'}")

        time.sleep(5)

except KeyboardInterrupt:
    print("\nProgram leállítva a felhasználó által.")
    GPIO.cleanup()
    blue_led.close()
    red_led.close()

         
       
