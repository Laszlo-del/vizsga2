import time
import random
import requests
from gpiozero import PWMLED
import RPi.GPIO as GPIO

# --- GPIO beállítások ---
GPIO.setmode(GPIO.BCM)
red_led = PWMLED(21)   # Piros LED: GPIO 21
blue_led = PWMLED(20)  # Kék LED: GPIO 20

# --- ThingSpeak beállítás ---
API_KEY = "6XC3DGU5D2YYL0PP"
THINGSPEAK_URL = "https://api.thingspeak.com/update"

# --- Kezdeti értékek ---
current_temperature = 18.0
current_humidity = 60.0

print("Szimuláció indult. Adatok ThingSpeak-re küldése...")

try:
    # 3 kezdeti ciklus: biztosan kék LED
    for i in range(3):
        red_led.value = 0
        blue_led.value = 1
        print(f"Kezdő állapot ({i+1}/3): Hőmérséklet: {current_temperature:.1f}°C, Páratartalom: {current_humidity:.1f}%")
        time.sleep(5)

    # --- Fő ciklus ---
    while True:
        # Szimulált hőmérséklet változás
        if current_temperature < 26.0:
            current_temperature += random.uniform(0.3, 0.7)
        else:
            current_temperature += random.uniform(-0.2, 0.2)

        # Szimulált páratartalom változás
        current_humidity += random.uniform(-0.5, 0.5)
        current_humidity = max(0, min(100, current_humidity))

        # LED vezérlés
        if current_temperature > 20:
            red_led.value = 1
            blue_led.value = 0
        else:
            red_led.value = 0
            blue_led.value = 1

        # --- Adatküldés ThingSpeak-re ---
        payload = {
            "api_key": API_KEY,
            "field1": round(current_temperature, 2),
            "field2": round(current_humidity, 2)
        }

        try:
            response = requests.post(THINGSPEAK_URL, data=payload, timeout=5)
            if response.status_code == 200:
                print(f"Küldve -> Hőmérséklet: {current_temperature:.2f}°C, Páratartalom: {current_humidity:.2f}%")
            else:
                print(f"HIBA! HTTP {response.status_code}")
        except requests.RequestException as e:
            print("Hálózati hiba:", e)

        time.sleep(15)  # 15 másodperc ThingSpeak limit miatt

except KeyboardInterrupt:
    print("\nProgram leállítva.")
    GPIO.cleanup()
    blue_led.close()
    red_led.close()
