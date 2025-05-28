import time
from gpiozero import PWMLED
import RPi.GPIO as GPIO
import Adafruit_DHT

GPIO.setmode(GPIO.BCM)

# --- PIN definíciók ---
DHT_PIN = 17
RED_LED_PIN = 21
BLUE_LED_PIN = 20

DHT_SENSOR = Adafruit_DHT.DHT11

red_led = PWMLED(RED_LED_PIN)
blue_led = PWMLED(BLUE_LED_PIN)

try:
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
            print(f"Hőmérséklet: {temperature:.1f}°C, Páratartalom: {humidity:.1f}%")
            print("Sikeres adatküldés.")

            if temperature <= 20:
                red_led.value = 1
                blue_led.value = 0
                print("A LED állapota: PIROS")
            else:
                red_led.value = 0
                blue_led.value = 1
                print("A LED állapota: KÉK")
        else:
            print("Szenzoradat olvasás sikertelen. Ellenőrizd a bekötést.")
            red_led.value = 0
            blue_led.value = 0
            print("A LED állapota: KI")

        time.sleep(10)

except KeyboardInterrupt:
    print("\nProgram leállítva felhasználó által.")
    red_led.value = 0
    blue_led.value = 0
    GPIO.cleanup()
