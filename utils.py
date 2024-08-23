import json, os, time, re

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
EXEMPT_IPS = ['127.0.0.1'] # Wyjątki od blokowania
START_TIME = time.time()
GEOIP_DATABASE = 'geo/GeoLite2-Country.mmdb'  # Ścieżka do pliku bazy danych GeoIP
DATA_DIR = 'data' # Katalog do przechowywania danych
PHOTOS_DIR = 'static/photos' # Katalog do przechowywania zdjęć
USERS_FILE = os.path.join(DATA_DIR, 'users.json') # Plik do przechowywania danych użytkowników
DATA_FILE = os.path.join(DATA_DIR, 'data.json') # Plik do przechowywania danych

entry_counter = 0
ip_blocks = 0
ip_blocks_unknown = 0

# Funkcja pomocnicza do wczytywania danych z pliku
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

# Funkcja pomocnicza do zapisywania danych do pliku
def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Uptime serwera i informacje do statusu
def get_uptime():
    return time.time() - START_TIME

# Walidacja wsp. geo.
def validate_lat_long(lat, long):
    try:
        lat = float(lat)
        long = float(long)
    except ValueError:
        return False
    return -90 <= lat <= 90 and -180 <= long <= 180

# Walidacja eMail
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# Walidacja kom.
def validate_phone(phone):
    return phone.isdigit() and len(phone) == 9