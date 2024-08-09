from flask import Flask, request, jsonify, render_template_string
import uuid
import base64
import os
import json
import folium
import pandas as pd
import logging
from logging.handlers import RotatingFileHandler
import geoip2.database
from werkzeug.exceptions import Forbidden
import time

start_time = time.time()
ip_blocks = 0
ip_blocks_unknown = 0
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

# Logowanie adresów IP
@app.before_request
def log_request_info():
    app.logger.info(f"Mamy gościa - Adres IP: {request.remote_addr}, URL: {request.url}, Metoda: {request.method}, User-Agent: {request.user_agent}")

# Blokowanie wejść spoza Polski
GEOIP_DATABASE = 'geo/GeoLite2-Country.mmdb'  # Ścieżka do pliku bazy danych GeoIP

if not os.path.exists(GEOIP_DATABASE):
    raise FileNotFoundError("Brak pliku bazy danych GeoIP. Upewnij się, że plik GeoLite2-Country.mmdb jest dostępny.")

geoip_reader = geoip2.database.Reader(GEOIP_DATABASE)
app.logger.info(f"Baza GeoIP załadowana")

@app.before_request
def block_non_polish_ips():
    try:
        response = geoip_reader.country(request.remote_addr)
        if response.country.iso_code != 'PL':
            app.logger.warning(f"Blokowane połączenie z adresu IP: {request.remote_addr} (kraj: {response.country.iso_code})")
            ip_blocks = ip_blocks + 1
            raise Forbidden(description="Dostęp zabroniony: połączenia spoza Polski są blokowane.")
    except geoip2.errors.AddressNotFoundError:
        app.logger.warning(f"Nieznany adres IP: {request.remote_addr}. Blokowanie połączenia.")
        ip_blocks_unknown = ip_blocks_unknown + 1
        raise Forbidden(description="Dostęp zabroniony: nieznany adres IP.")

# Katalog do przechowywania danych
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Plik do przechowywania danych
DATA_FILE = os.path.join(DATA_DIR, 'data.json')

# Funkcja pomocnicza do wczytywania danych z pliku
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return []

# Funkcja pomocnicza do zapisywania danych do pliku
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Uptime serwera i informacje do statusu
def get_uptime():
    return time.time() - start_time

@app.route('/status', methods=['GET'])
def status():
    data = load_data()
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
        'ip_blocks': ip_blocks,
        'ip_blocks_unknown': ip_blocks_unknown,
        'uptime': uptime_str
    }

    return jsonify(status_info), 200

# Wczytywanie wysłanych danych
@app.route('/upload', methods=['POST'])
def upload():
    content = request.json
    entry_id = content.get('id')
    data = content.get('data')
    opis = content.get('opis')
    zdjecie_base64 = content.get('zdjecie')
    latitude = content.get('latitude')
    longitude = content.get('longitude')

    if not all([data, opis, zdjecie_base64, latitude, longitude]):
        return jsonify({'error': 'Brakuje data, opis, zdjecie, latitude lub longitude'}), 400

    # Wczytanie dotychczasowych danych
    existing_data = load_data()

    if entry_id:
        # Sprawdzanie czy ID istnieje
        if not any(entry['id'] == entry_id for entry in existing_data):
            return jsonify({'error': 'Błędny ID. Należy wysłać pierwszą wiadomość bez ID, aby otrzymać nowy ID.'}), 400
    else:
        # Generowanie nowego ID
        entry_id = str(uuid.uuid4())

    # Dekodowanie i zapisywanie zdjęcia
    try:
        zdjecie_bytes = base64.b64decode(zdjecie_base64)
    except base64.binascii.Error:
        return jsonify({'error': 'Błędne dane base64'}), 400

    zdjecie_filename = os.path.join(DATA_DIR, f"{data.replace(':', '-')}.jpg")
    with open(zdjecie_filename, 'wb') as zdjecie_file:
        zdjecie_file.write(zdjecie_bytes)

    # Dodanie nowych danych
    new_entry = {
        'id': entry_id,
        'data': data,
        'opis': opis,
        'zdjecie': zdjecie_filename,
        'latitude': latitude,
        'longitude': longitude
    }

    existing_data.append(new_entry)
    save_data(existing_data)

    return jsonify({'message': 'Dane zapisane pomyślnie', 'id': entry_id}), 200

# Pobieranie zapisanych danych
@app.route('/data', methods=['GET'])
def get_data():
    entry_id = request.args.get('id')
    data = load_data()

    if entry_id:
        data = [entry for entry in data if entry['id'] == entry_id]
        if not data:
            return jsonify({'error': 'Nie znaleziono danych dla podanego ID'}), 404
    else:
        data = [{k: v for k, v in entry.items() if k != 'id'} for entry in data]

    return jsonify(data), 200

# Wizualizacja danych na mapie
@app.route('/map', methods=['GET'])
def map_view():
    entry_id = request.args.get('id')
    data = load_data()

    if entry_id:
        data = [entry for entry in data if entry['id'] == entry_id]
        if not data:
            return render_template_string("""
                <html>
                <head>
                    <title>Mapa zgłoszeń</title>
                </head>
                <body>
                    <h1>Nie znaleziono danych dla podanego ID</h1>
                </body>
                </html>
            """)
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
    return render_template_string("""
        <html>
        <head>
            <title>Mapa zgłoszeń</title>
        </head>
        <body>
            {{ map_html|safe }}
        </body>
        </html>
    """, map_html=map_html)

# Podgląd danych
@app.route('/table', methods=['GET'])
def table_view():
    data = load_data()
    df = pd.DataFrame(data)
    table_html = df.to_html(classes='table table-striped', index=False)
    return render_template_string("""
        <html>
        <head>
            <title>Zestawienie zgłoszeń</title>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
        </head>
        <body>
            {{ table_html|safe }}
        </body>
        </html>
    """, table_html=table_html)

# Pomoc i opis do API REST
@app.route('/help', methods=['GET'])
def help_view():
    help_text = """
    <html>
    <head>
        <title>Pomoc API</title>
    </head>
    <body>
        <h1>Pomoc API</h1>
        <h2>Endpoint: /upload</h2>
        <p>Metoda: POST</p>
        <p>Opis: Endpoint służy do przesyłania danych wraz z obrazem. Dane są zapisywane na serwerze.</p>
        <p>Body (JSON):</p>
        <pre>{
    "data": "2021-08-06",
    "opis": "Opis zdjęcia",
    "zdjecie": "base64kodowanyObraz",
    "latitude": 54.7578,
    "longitude": 17.5610
}</pre>
        <p>Odpowiedź:</p>
        <pre>{
    "message": "Dane zapisane pomyślnie"
}</pre>

        <h2>Endpoint: /data</h2>
        <p>Metoda: GET</p>
        <p>Opis: Endpoint zwraca wszystkie zapisane dane w formacie JSON.</p>
        <p>Odpowiedź:</p>
        <pre>[
    {
        "data": "2021-08-06",
        "opis": "Opis zdjęcia",
        "zdjecie": "data/2021-08-06.jpg",
        "latitude": 54.7578,
        "longitude": 17.5610
    },
    ...
]</pre>
    </body>
    </html>
    """
    return render_template_string(help_text)

if __name__ == '__main__':
    app.run(debug=True, port=20162)
