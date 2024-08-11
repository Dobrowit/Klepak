import uuid
import base64
import os
import json
import folium
import pandas as pd
import logging
import time
import io
import re
import geoip2.database
from flask import Flask, request, jsonify, render_template_string, render_template
from logging.handlers import RotatingFileHandler
from werkzeug.exceptions import Forbidden
from werkzeug.utils import secure_filename
from PIL import Image

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
EXEMPT_IPS = ['127.0.0.1']
START_TIME = time.time()
IP_BLOCKS = 0
IP_BLOCKS_UNKNOWN = 0
ENTRY_COUNTER = 0
GEOIP_DATABASE = 'geo/GeoLite2-Country.mmdb'  # Ścieżka do pliku bazy danych GeoIP
DATA_DIR = 'data' # Katalog do przechowywania danych
USERS_FILE = os.path.join(DATA_DIR, 'users.json') # Plik do przechowywania danych użytkowników
DATA_FILE = os.path.join(DATA_DIR, 'data.json') # Plik do przechowywania danych
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
if not os.path.exists(GEOIP_DATABASE):
    raise FileNotFoundError("Brak pliku bazy danych GeoIP. Upewnij się, że plik GeoLite2-Country.mmdb jest dostępny.")

app = Flask(__name__)

# Dziennik
if not os.path.exists('logs'):
    os.mkdir('logs')

file_handler = RotatingFileHandler('logs/klepak.log', maxBytes=102400, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Klepak startup')

# Ładowanie bazy GeoIP
geoip_reader = geoip2.database.Reader(GEOIP_DATABASE)
app.logger.info(f"Baza GeoIP załadowana")

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

# Logowanie adresów IP
@app.before_request
def log_request_info():
    global ENTRY_COUNTER
    ENTRY_COUNTER += 1
    app.logger.info(f"Mamy gościa - Adres IP: {request.remote_addr}, URL: {request.url}, Metoda: {request.method}, User-Agent: {request.user_agent}")

# Blokowanie wejść spoza Polski
@app.before_request
def block_non_polish_ips():
    global IP_BLOCKS, IP_BLOCKS_UNKNOWN

    if request.remote_addr in EXEMPT_IPS:
        app.logger.info(f"Adres IP: {request.remote_addr} znajduje się na liście wyjątków, dostęp przyznany.")
        return  # Przejdź dalej bez blokowania
    try:
        response = geoip_reader.country(request.remote_addr)
        if response.country.iso_code != 'PL':
            app.logger.warning(f"Blokowane połączenie z adresu IP: {request.remote_addr} (kraj: {response.country.iso_code})")
            IP_BLOCKS += 1
            raise Forbidden(description="Dostęp zabroniony: połączenia spoza Polski są blokowane.")
    except geoip2.errors.AddressNotFoundError:
        app.logger.warning(f"Nieznany adres IP: {request.remote_addr}. Blokowanie połączenia.")
        IP_BLOCKS_UNKNOWN += 1
        raise Forbidden(description="Dostęp zabroniony: nieznany adres IP.")

@app.route('/status', methods=['GET'])
def status():
    data = load_data(DATA_FILE)
    num_entries = len(data)
    num_images = len([name for name in os.listdir(DATA_DIR) if name.endswith('.jpg') and os.path.isfile(os.path.join(DATA_DIR, name))])

    data_file_size = os.path.getsize(DATA_FILE) if os.path.exists(DATA_FILE) else 0
    images_size = sum(os.path.getsize(os.path.join(DATA_DIR, name)) for name in os.listdir(DATA_DIR) if name.endswith('.jpg') and os.path.isfile(os.path.join(DATA_DIR, name)))

    total_size_mb = round((data_file_size + images_size) / (1024 * 1024), 1)
    data_file_size = round(data_file_size / (1024 * 1024), 1)
    images_size = round(images_size / (1024 * 1024), 1)

    uptime_seconds = int(get_uptime())
    uptime_str = f"{uptime_seconds // 3600}h {uptime_seconds % 3600 // 60}m {uptime_seconds % 60}s"

    status_info = {
        'num_entries': num_entries,
        'num_images': num_images,
        'data_file_size': data_file_size,
        'images_files_size': images_size,
        'total_size_mb': total_size_mb,
        'ip_blocks': IP_BLOCKS,
        'ip_blocks_unknown': IP_BLOCKS_UNKNOWN,
        'entry_counter': ENTRY_COUNTER,
        'uptime': uptime_str
    }

    return jsonify(status_info), 200

# Rejestracja użytkownika
@app.route('/register', methods=['POST'])
def register():
    content = request.json
    imie = content.get('imie')
    nazwisko = content.get('nazwisko')
    email = content.get('email')
    phone = content.get('phone')

    if not all([email, phone]):
        return jsonify({'error': 'Brakuje jednego z wymaganych pól: email, nr tel.'}), 400

    # Walidacja formatu email i numeru telefonu
    if not validate_email(email):
        return jsonify({'error': 'Niepoprawny format adresu email'}), 400
    if not validate_phone(phone):
        return jsonify({'error': 'Niepoprawny format numeru telefonu (wymagane 9 cyfr)'}), 400

    # Wczytanie dotychczasowych danych użytkowników
    try:
        users = load_data(USERS_FILE)
    except IOError as e:
        app.logger.error(f"Błąd przy wczytywaniu danych użytkowników: {str(e)}")
        return jsonify({'error': 'Błąd serwera przy rejestracji'}), 500
    
    # Sprawdzenie unikalności email i numeru telefonu
    if any(user['email'] == email for user in users):
        return jsonify({'error': 'Email jest już zarejestrowany'}), 400
    if any(user['phone'] == phone for user in users):
        return jsonify({'error': 'Numer telefonu jest już zarejestrowany'}), 400
    
    user_id = str(uuid.uuid4())
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

    new_user = {
        'id': user_id,
        'imie': imie,
        'nazwisko': nazwisko,
        'email': email,
        'phone': phone,
        'data': timestamp
    }

    users.append(new_user)

    try:
        save_data(USERS_FILE, users)
    except IOError as e:
        app.logger.error(f"Błąd przy zapisywaniu danych użytkowników: {str(e)}")
        return jsonify({'error': 'Błąd serwera przy rejestracji'}), 500
    
    return jsonify({'message': 'Użytkownik zarejestrowany pomyślnie', 'id': user_id}), 201

# Wczytywanie wysłanych danych
@app.route('/upload', methods=['POST'])
def upload():
    content = request.json
    user_id = content.get('id')
    data = content.get('data')
    opis = content.get('opis')
    zdjecie_base64 = content.get('zdjecie')
    latitude = content.get('latitude')
    longitude = content.get('longitude')

    if not user_id:
        return jsonify({'error': 'Brak ID użytkownika'}), 400
    
    if not validate_lat_long(latitude, longitude):
        return jsonify({'error': 'Nieprawidłowe współrzędne geograficzne.'}), 400

    if not all([data, opis, zdjecie_base64, latitude, longitude]):
        return jsonify({'error': 'Brakuje data, opis, zdjecie, latitude lub longitude'}), 400

    # Limit długości opisu
    if len(opis) > 5000:  # przykładowy limit 1000 znaków
        return jsonify({'error': 'Opis jest zbyt długi (max 5000 znaków)'}), 400
    
    # Wczytanie dotychczasowych danych użytkowników
    try:
        users = load_data(USERS_FILE)
    except IOError as e:
        app.logger.error(f"Błąd przy wczytywaniu danych użytkowników: {str(e)}")
        return jsonify({'error': 'Błąd serwera przy uploadzie'}), 500

    # Sprawdzenie, czy ID jest zarejestrowane
    if not any(user['id'] == user_id for user in users):
        return jsonify({'error': 'Błędny ID. Użytkownik niezarejestrowany.'}), 400

    # Wczytanie dotychczasowych danych
    try:
        existing_data = load_data(DATA_FILE)
    except IOError as e:
        app.logger.error(f"Błąd przy wczytywaniu istniejących danych: {str(e)}")
        return jsonify({'error': 'Błąd serwera przy uploadzie'}), 500
    
    # Dekodowanie i zapisywanie zdjęcia
    try:
        zdjecie_bytes = base64.b64decode(zdjecie_base64)
        if len(zdjecie_bytes) > MAX_IMAGE_SIZE:
            return jsonify({'error': 'Plik jest za duży, maksymalny rozmiar to 5 MB.'}), 400
    except base64.binascii.Error:
        return jsonify({'error': 'Błędne dane base64'}), 400

    # Generowanie unikalnej nazwy pliku
    timestamp = int(time.time() * 1000)
    zdjecie_filename = secure_filename(f"{timestamp}_{user_id}.jpg")
    zdjecie_path = os.path.join(DATA_DIR, zdjecie_filename)

    try:
        with open(zdjecie_path, 'wb') as zdjecie_file:
            zdjecie_file.write(zdjecie_bytes)
    except IOError as e:
        app.logger.error(f"Błąd przy zapisywaniu zdjęcia: {str(e)}")
        return jsonify({'error': 'Błąd serwera przy zapisywaniu zdjęcia'}), 500

    # Dodanie nowych danych
    new_entry = {
        'id': user_id,
        'data': data,
        'opis': opis,
        'zdjecie': zdjecie_filename,
        'latitude': latitude,
        'longitude': longitude
    }

    existing_data.append(new_entry)

    try:
        save_data(DATA_FILE, existing_data)
    except IOError as e:
        app.logger.error(f"Błąd przy zapisywaniu danych: {str(e)}")
        return jsonify({'error': 'Błąd serwera przy zapisywaniu danych'}), 500

    return jsonify({'message': 'Dane zapisane pomyślnie', 'id': user_id}), 200

# Pobieranie zapisanych danych
@app.route('/data', methods=['GET'])
def get_data():
    entry_id = request.args.get('id')
    data = load_data(DATA_FILE)

    if entry_id:
        data = [entry for entry in data if entry['id'] == entry_id]
        if not data:
            return jsonify({'error': 'Nie znaleziono danych dla podanego ID'}), 404
    else:
        data = [{k: v for k, v in entry.items() if k != 'id'} for entry in data]

    return jsonify(data), 200

@app.route('/map', methods=['GET'])
def map_view():
    entry_id = request.args.get('id')
    data = load_data(DATA_FILE)

    if entry_id:
        data = [entry for entry in data if entry['id'] == entry_id]
        if not data:
            return render_template('map-error.html')
    else:
        data = [{k: v for k, v in entry.items() if k != 'id'} for entry in data]

    map_ = folium.Map(location=[54.7578, 17.5610], zoom_start=15)
    for entry in data:
        folium.Marker(
            location=[entry['latitude'], entry['longitude']],
            popup=f"{entry['data']}: {entry['opis']}",
            tooltip=entry['opis']
        ).add_to(map_)

    map_html = map_._repr_html_()
    return render_template('map.html', map_html=map_html)

# Podgląd danych
@app.route('/table', methods=['GET'])
def table_view():
    data = load_data(DATA_FILE)
    df = pd.DataFrame(data)
    table_html = df.to_html(classes='table table-striped', index=False)
    return render_template('table.html', table_html=table_html)

# Pomoc i opis do API REST
@app.route('/help', methods=['GET'])
def help_view():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True, port=20162)
