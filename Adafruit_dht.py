import requests
import time
from gpiozero import PWMLED 
import RPi.GPIO as GPIO
import Adafruit_DHT

# GPIO beállítások (BCM mód)
GPIO.setmode(GPIO.BCM)

# DHT11 szenzor inicializálása
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 17  # GPIO 17 (fizikai pin 11)

# LED-ek GPIO pin-ekhez
red_led = PWMLED(21)   # Piros LED
blue_led = PWMLED(20)  # Kék LED

# ThingSpeak API kulcs
API_KEY = 'G6SD9SSNQ1VACKKH'

def send_data_to_thingspeak(temp, humid):
    url = f'https://api.thingspeak.com/update?api_key={API_KEY}&field1={temp}&field2={humid}'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"Adat elküldve: Hőmérséklet={temp:.1f}°C, Páratartalom={humid:.1f}%")
        else:
            print(f"Hiba az adatküldésnél: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Hálózati hiba: {e}")

try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
            print(f"Hőmérséklet: {temperature:.1f}°C, Páratartalom: {humidity:.1f}%")

            # LED vezérlés: <=20 fok PIROS, >20 KÉK
            if temperature <= 20:
                red_led.value = 1
                blue_led.value = 0
            else:
                red_led.value = 0
                blue_led.value = 1

            send_data_to_thingspeak(temperature, humidity)
        else:
            print("Nem sikerült olvasni a szenzort. Ellenőrizd a bekötést!")

        time.sleep(15)  # 15 mp a ThingSpeak limit miatt

except KeyboardInterrupt:
    print("\nProgram leállítva.")
    GPIO.cleanup()
    red_led.close()
    blue_led.close()
