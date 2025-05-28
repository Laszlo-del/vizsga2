import requests
import datetime
import time # Bár a kódban nincs közvetlenül használva, jó ha itt van a date/time műveletek miatt

# --- Konfiguráció ---
CHANNEL_ID = '2974172'  # A ThingSpeak csatornád ID-ja
USER_API_KEY = 'IWD8FW50D4CUAHW4'  # A felhasználói API kulcsod (User API Key)

# A törlési API végpont URL-je
url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"

def torol_utolso_2_percet():
    # Az aktuális idő mínusz 2 perc. Ez a dátum lesz a törlési intervallum vége.
    # Minden adat, ami EZELŐTT az időpont előtt érkezett, törlődik.
    delete_before_date = datetime.datetime.now() - datetime.timedelta(minutes=2)

    # A kérés paraméterei a Thingspeak API számára
    params = {
        'api_key': USER_API_KEY,
        'end': delete_before_date.isoformat(sep=' ', timespec='seconds') # ISO 8601 formátumú dátum
    }

    print(f"Adatok törlése a {CHANNEL_ID} csatornáról az utolsó 2 percben érkezett bejegyzésekig ({delete_before_date} előtt).")
    print("Kérlek, ellenőrizd a User API Key-t és a Channel ID-t!")

    try:
        # HTTP DELETE kérés küldése a Thingspeak API-nak
        response = requests.delete(url, params=params)

        # Válasz kiértékelése
        if response.status_code == 200:
            print("✅ Adatok sikeresen törölve!")
            # A válasz tartalmát kiírhatod, ha hibakeresésnél hasznos (pl. '0' sikeres törlés esetén)
            # print(f"Válasz: {response.text}")
        else:
            # Hiba esetén kiírja a státuszkódot és a ThingSpeak hibaüzenetét
            print(f"❌ Hiba történt. Státuszkód: {response.status_code}. Üzenet: {response.text}")

    except requests.exceptions.RequestException as e:
        # Hálózati vagy egyéb kérés-specifikus hiba esetén
        print(f"⚠️ Hálózati hiba: {e}")

# A funkció meghívása a szkript futtatásakor
torol_utolso_2_percet()
