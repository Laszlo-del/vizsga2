import time
from gpiozero import PWMLED
import Adafruit_DHT
import RPi.GPIO as GPIO

# GPIO mód beállítása (BCM számozás)
GPIO.setmode(GPIO.BCM)

# DHT szenzor típus és GPIO pin definiálása
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 17 # A DHT11 szenzor a 17-es GPIO lábra van kötve

# Hőmérsékleti limit, ami alapján a LED színe változik
TEMP_LIMIT = 20

# Elérhető LED színek listája
COLORS = ['piros', 'zöld', 'kék']

# Alapértelmezett GPIO kiosztás a piros, zöld, kék LED-ekhez
gpio_pins = {
    'piros': 21,
    'zöld': 16,
    'kék': 20
}

# Alapértelmezett színbeállítások a hőmérsékleti határokhoz
led_below = 'piros' # <=20°C esetén piros
led_above = 'kék'   # >20°C esetén kék

# LED példányok tárolására szolgáló szótár (üresen indul)
leds = {}

# Funkció: LED példányok inicializálása a jelenlegi GPIO beállítások alapján
def init_leds():
    global leds
    # Biztosítja, hogy a korábbi LED objektumok megfelelően legyenek leállítva, ha újra inicializálunk
    for led in leds.values():
        led.close() # Felszabadítja a GPIO erőforrásokat
    leds = {
        'piros': PWMLED(gpio_pins['piros']),
        'zöld': PWMLED(gpio_pins['zöld']),
        'kék': PWMLED(gpio_pins['kék'])
    }
    print("✅ LED-ek inicializálva az új GPIO-kkal.")

# Funkció: A megfelelő LED szín bekapcsolása
def set_led(color):
    # Minden LED kikapcsolása
    for led in leds.values():
        led.value = 0
    # A kiválasztott színű LED bekapcsolása (1-es értékkel, ami teljes fényerő)
    if color in leds:
        leds[color].value = 1
        print(f"🔔 LED: {color.upper()} ({'<=20°C' if color == led_below else '>20°C'})")
    else:
        print(f"⚠️ Hibás LED szín megadva: {color}")

# Funkció: GPIO portok módosítása felhasználói bevitel alapján
def change_gpio():
    print("\n🎛️ GPIO módosítás:")
    for color in COLORS:
        try:
            # Bekéri a felhasználótól az új GPIO pin számot
            pin = int(input(f"{color.upper()} LED GPIO (jelenleg {gpio_pins[color]}): "))
            gpio_pins[color] = pin
        except ValueError:
            print("⚠️ Hibás érték, megtartva a régi GPIO-t.")
    print("✅ GPIO-k frissítve.")
    init_leds() # Újra inicializálja a LED példányokat az új GPIO-kkal

# Funkció: A hőmérséklethez tartozó LED színek beállítása
def change_behavior():
    global led_below, led_above
    print("\n🎨 LED színek beállítása a hőmérséklet alapján:")
    # Bekéri a kívánt színeket
    led_below_input = input("20°C alatt milyen LED szín legyen (piros/zöld/kék): ").strip().lower()
    led_above_input = input("20°C felett milyen LED szín legyen (piros/zöld/kék): ").strip().lower()

    # Ellenőrzi, hogy érvényes színek lettek-e megadva
    if led_below_input in COLORS and led_above_input in COLORS:
        led_below = led_below_input
        led_above = led_above_input
        print(f"✅ Beállítva: <=20°C ➜ {led_below.upper()}, >20°C ➜ {led_above.upper()}")
    else:
        print("⚠️ Hibás szín! Visszaállítás alapértelmezett értékekre (piros / kék).")
        led_below, led_above = 'piros', 'kék'

# Funkció: Szenzor adatgyűjtés és LED-vezérlés indítása
def run_sensor_loop():
    print("\n▶️ Indítás... Nyomj CTRL+C-t a kilépéshez.")
    try:
        while True:
            # Hőmérséklet és páratartalom olvasása a DHT11 szenzorról
            humidity, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            if temp is not None:
                # Adatok kiírása a konzolra
                print(f"\n🌡️ Hőmérséklet: {temp:.1f}°C, 💧 Páratartalom: {humidity:.1f}%")
                # LED szín kiválasztása a hőmérséklet alapján
                if temp <= TEMP_LIMIT:
                    set_led(led_below)
                else:
                    set_led(led_above)
            else:
                print("❌ Szenzorhiba! Ellenőrizd a bekötést és a szenzort.")
                # Minden LED kikapcsolása hiba esetén
                for led in leds.values():
                    led.value = 0
            time.sleep(10) # Várakozás 10 másodpercet a következő mérésig

    except KeyboardInterrupt:
        print("\n🛑 Kilépés...")
    finally:
        # Program befejezésekor a GPIO lábak tisztítása
        GPIO.cleanup()

# Főmenü megjelenítése és a felhasználói választások kezelése
def main_menu():
    init_leds() # A LED-ek inicializálása a program elején
    while True:
        print("\n📋 Főmenü:")
        print("1. GPIO portok módosítása")
        print("2. Színek beállítása 20°C alatt/felett")
        print("3. LED-vezérlés indítása")
        print("4. Kilépés")

        choice = input("Választás (1-4): ").strip()
        if choice == '1':
            change_gpio()
        elif choice == '2':
            change_behavior()
        elif choice == '3':
            run_sensor_loop()
            # Ha a run_sensor_loop lefutott (pl. CTRL+C miatt), visszatér a főmenübe
        elif choice == '4':
            print("👋 Kilépés...")
            GPIO.cleanup() # Kilépéskor is tisztítja a GPIO-kat
            break
        else:
            print("❌ Érvénytelen választás. Kérlek, válassz 1 és 4 között.")

# A program indítása a főmenüvel
if __name__ == "__main__":
    main_menu()
