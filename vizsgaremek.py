import time
from gpiozero import PWMLED
import Adafruit_DHT
import RPi.GPIO as GPIO
import requests # A Thingspeakhez szükséges
import datetime # Az időbélyegekhez és a törléshez

# --- GPIO beállítások ---
GPIO.setmode(GPIO.BCM)

# --- DHT Szenzor beállítások ---
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 17 # Alapértelmezett DHT11 szenzor GPIO pin

# --- Hőmérsékleti limit a LED jelzéshez ---
TEMP_LIMIT = 20

# --- LED színek listája ---
COLORS = ['piros', 'zöld', 'kék']

# --- Alapértelmezett GPIO kiosztás a LED-ekhez ---
gpio_pins = {
    'piros': 21,
    'zöld': 16,
    'kék': 20
}

# --- Alapértelmezett LED szín viselkedés ---
led_below_limit = 'piros' # <= TEMP_LIMIT esetén
led_above_limit = 'kék'   # > TEMP_LIMIT esetén

# --- Thingspeak beállítások ---
THINGSPEAK_WRITE_API_KEY = 'IDE_JON_A_SAJAT_WRITE_API_KULCSOD' # Ezt a csatornád oldalán találod
THINGSPEAK_USER_API_KEY = 'IDE_JON_A_SAJAT_USER_API_KULCSOD'   # Ezt az 'Account' -> 'My Profile' alatt találod
THINGSPEAK_CHANNEL_ID = 'IDE_JON_A_SAJAT_CSATORNA_ID_D'        # Ezt a csatornád oldalán találod
THINGSPEAK_URL = "https://api.thingspeak.com/update"
THINGSPEAK_DELETE_URL_BASE = "https://api.thingspeak.com/channels/"

# LED példányok tárolása
leds = {}

# --- Segédfüggvények ---

def init_leds():
    """Inicializálja a LED-eket a jelenlegi GPIO beállítások alapján, vagy frissíti azokat."""
    global leds
    for led in leds.values():
        led.close() # Felszabadítja a korábbi GPIO erőforrásokat
    leds = {
        'piros': PWMLED(gpio_pins['piros']),
        'zöld': PWMLED(gpio_pins['zöld']),
        'kék': PWMLED(gpio_pins['kék'])
    }
    print("✅ LED-ek inicializálva az új GPIO-kkal.")

def set_led(color):
    """Beállítja a megadott színű LED-et, a többit kikapcsolja."""
    for led in leds.values():
        led.value = 0 # Minden LED kikapcsolása
    if color in leds:
        leds[color].value = 1 # A kiválasztott LED bekapcsolása
        print(f"🔔 LED: {color.upper()} ({'<=20°C' if color == led_below_limit else '>20°C'})")
    else:
        print(f"⚠️ Hibás LED szín megadva: {color}")

def send_to_thingspeak(temp, hum):
    """Elküldi a hőmérsékletet és páratartalmat a Thingspeakre."""
    if not THINGSPEAK_WRITE_API_KEY or not THINGSPEAK_CHANNEL_ID:
        print("❌ Thingspeak API kulcs vagy csatorna ID hiányzik. Adatküldés kihagyva.")
        return

    try:
        payload = {
            'api_key': THINGSPEAK_WRITE_API_KEY,
            'field1': temp, # Első mező a hőmérsékletnek
            'field2': hum    # Második mező a páratartalomnak
        }
        response = requests.get(THINGSPEAK_URL, params=payload)

        if response.status_code == 200:
            print("⬆️ Adatok elküldve Thingspeakre.")
        else:
            print(f"❌ Hiba a Thingspeak küldéskor: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Hálózati hiba a Thingspeak küldéskor: {e}")

def delete_thingspeak_data(minutes_ago):
    """Törli az adatokat a Thingspeakről egy megadott időintervallumból."""
    if not THINGSPEAK_USER_API_KEY or not THINGSPEAK_CHANNEL_ID:
        print("❌ Thingspeak User API kulcs vagy csatorna ID hiányzik. Törlés kihagyva.")
        return

    # Törlés az aktuális idő mínusz 'minutes_ago' időpontig
    delete_before_date = datetime.datetime.now() - datetime.timedelta(minutes=minutes_ago)

    delete_url = f"{THINGSPEAK_DELETE_URL_BASE}{THINGSPEAK_CHANNEL_ID}/feeds.json"
    params = {
        'api_key': THINGSPEAK_USER_API_KEY,
        'end': delete_before_date.isoformat(sep=' ', timespec='seconds')
    }

    print(f"Adatok törlése a {THINGSPEAK_CHANNEL_ID} csatornáról {minutes_ago} perccel ezelőtti időpontig ({delete_before_date} előtt).")
    try:
        response = requests.delete(delete_url, params=params)

        if response.status_code == 200:
            print("✅ Adatok sikeresen törölve a Thingspeakről!")
        else:
            print(f"❌ Hiba a Thingspeak törléskor: {response.status_code} - {response.text}")
            print("Tipp: Ellenőrizd a USER_API_KEY-t, az kell a törléshez!")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Hálózati hiba a Thingspeak törléskor: {e}")

# --- Konfigurációs menüpontok ---

def change_gpio_pins():
    """Lehetővé teszi a LED GPIO portjainak módosítását."""
    print("\n🎛️ GPIO portok módosítása:")
    for color in COLORS:
        try:
            pin = int(input(f"{color.upper()} LED GPIO (jelenleg {gpio_pins[color]}): "))
            gpio_pins[color] = pin
        except ValueError:
            print("⚠️ Hibás érték, megtartva a régi GPIO-t.")
    init_leds() # Újra inicializálja a LED-eket az új pinekkel

def change_led_behavior():
    """Lehetővé teszi a hőmérséklethez tartozó LED színek beállítását."""
    global led_below_limit, led_above_limit
    print("\n🎨 LED színek beállítása a hőmérséklet alapján (20°C a határ):")
    below_input = input("20°C alatt milyen LED szín legyen (piros/zöld/kék): ").strip().lower()
    above_input = input("20°C felett milyen LED szín legyen (piros/zöld/kék): ").strip().lower()

    if below_input in COLORS and above_input in COLORS:
        led_below_limit = below_input
        led_above_limit = above_input
        print(f"✅ Beállítva: <=20°C ➜ {led_below_limit.upper()}, >20°C ➜ {led_above_limit.upper()}")
    else:
        print("⚠️ Hibás szín! Visszaállítás alapértelmezettre (piros / kék).")
        led_below_limit, led_above_limit = 'piros', 'kék'

def change_thingspeak_settings():
    """Lehetővé teszi a Thingspeak beállítások módosítását."""
    global THINGSPEAK_CHANNEL_ID, THINGSPEAK_WRITE_API_KEY, THINGSPEAK_USER_API_KEY
    print("\n☁️ Thingspeak beállítások módosítása:")
    THINGSPEAK_CHANNEL_ID = input(f"Thingspeak csatorna ID (jelenleg {THINGSPEAK_CHANNEL_ID}): ").strip()
    THINGSPEAK_WRITE_API_KEY = input(f"Thingspeak Író API kulcs (jelenleg {THINGSPEAK_WRITE_API_KEY}): ").strip()
    THINGSPEAK_USER_API_KEY = input(f"Thingspeak Felhasználói API kulcs (jelenleg {THINGSPEAK_USER_API_KEY}): ").strip()
    print("✅ Thingspeak beállítások frissítve.")

def perform_thingspeak_data_delete():
    """Bekéri a törlendő időtartamot és végrehajtja a törlést."""
    try:
        minutes = int(input("Hány perccel ezelőtti adatokat töröljük? (pl. 5 perc az utolsó 5 percet törli): "))
        if minutes >= 0:
            delete_thingspeak_data(minutes)
        else:
            print("⚠️ Érvénytelen időtartam, pozitív számot adj meg!")
    except ValueError:
        print("⚠️ Hibás érték, csak számot adj meg!")

# --- Fő működési ciklus ---

def run_sensor_loop_and_thingspeak():
    """Futtatja a szenzor olvasást, LED vezérlést és Thingspeak küldést."""
    print("\n▶️ Rendszer indítása... Nyomj CTRL+C-t a kilépéshez.")
    try:
        while True:
            humidity, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            if temp is not None:
                print(f"\n🌡️ Hőmérséklet: {temp:.1f}°C, 💧 Páratartalom: {humidity:.1f}%")
                # LED beállítása
                if temp <= TEMP_LIMIT:
                    set_led(led_below_limit)
                else:
                    set_led(led_above_limit)
                # Adatok küldése Thingspeakre
                send_to_thingspeak(temp, humidity)
            else:
                print("❌ Szenzorhiba! Ellenőrizd a bekötést és a szenzort.")
                for led in leds.values():
                    led.value = 0 # Minden LED kikapcsolása hiba esetén
            time.sleep(15) # Várakozás 15 másodperc a következő mérésig

    except KeyboardInterrupt:
        print("\n🛑 Kilépés a ciklusból...")
    except Exception as e:
        print(f"Hiba történt a futás közben: {e}")
    finally:
        # A ciklusból való kilépéskor mindig tisztítja a GPIO-t
        GPIO.cleanup()
        for led in leds.values():
            led.close() # Biztosítja a LED objektumok bezárását is

# --- Főmenü ---

def main_menu():
    """Megjeleníti a főmenüt és kezeli a felhasználói interakciókat."""
    init_leds() # LED-ek inicializálása program indításakor
    while True:
        print("\n=== SmartTempHub Főmenü ===")
        print("1. GPIO portok módosítása")
        print("2. LED színek beállítása hőmérséklet alapján")
        print("3. Thingspeak beállítások módosítása")
        print("4. Thingspeak adatok törlése (időalapú)")
        print("5. Rendszer indítása (Szenzor + LED + Thingspeak)")
        print("6. Kilépés")

        choice = input("Válasszon (1-6): ").strip()

        if choice == '1':
            change_gpio_pins()
        elif choice == '2':
            change_led_behavior()
        elif choice == '3':
            change_thingspeak_settings()
        elif choice == '4':
            perform_thingspeak_data_delete()
        elif choice == '5':
            run_sensor_loop_and_thingspeak()
            # Ha a futás befejeződött (pl. CTRL+C miatt), visszatér a főmenübe
            init_leds() # Újra inicializálja a LED-eket a menübe való visszatéréskor
        elif choice == '6':
            print("👋 Kilépés a programból...")
            GPIO.cleanup() # Kilépéskor is tisztítja a GPIO-kat
            for led in leds.values():
                led.close()
            break
        else:
            print("❌ Érvénytelen választás. Kérlek, válassz 1 és 6 között.")

# A program indítása a főmenüvel
if __name__ == "__main__":
    main_menu()
