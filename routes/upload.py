from flask import Blueprint, request, jsonify
from utils import load_data, save_data, validate_lat_long, load_polygon_from_kml, is_point_in_polygon, USERS_FILE, DATA_FILE, PHOTOS_DIR, MAX_IMAGE_SIZE
import base64, os, time
from werkzeug.utils import secure_filename
import app
from datetime import datetime
from shapely.geometry import Point, Polygon
from fastkml import kml

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload():
    content = request.json
    user_id = content.get('Id')
    opis = content.get('Message')
    zdjecie_base64 = content.get('Base64Image')
    latitude = content.get('Latitude')
    longitude = content.get('Longitude')
    kategoria = content.get('Category')

    if not user_id:
        return jsonify({'error': 'Brak ID użytkownika'}), 400
    
    if not validate_lat_long(latitude, longitude):
        return jsonify({'error': 'Nieprawidłowe współrzędne geograficzne.'}), 400

    if not all([zdjecie_base64, latitude, longitude, kategoria]):
        return jsonify({'error': 'Brakuje zdjecie, latitude, longitude lub kategoria'}), 400

    # Limit długości opisu
    if len(opis) > 5000:  # przykładowy limit 1000 znaków
        return jsonify({'error': 'Opis jest zbyt długi (max 5000 znaków)'}), 400

    # Sprawdzanie czy jest w strefie
    kml_file_path = 'data/gmina.kml'
    polygon = load_polygon_from_kml(kml_file_path)
    latitude = content.get('Latitude')
    longitude = content.get('Longitude')

    if polygon:
        is_within_polygon = is_point_in_polygon(latitude, longitude, polygon)
        if not is_within_polygon:
            jsonify({'error': 'Punkt znajduje się poza obsługiwanym obszarem!'}), 400
    else:
        app.logger.error(f"Nie udało się załadować wielokąta z pliku KML.")
        return jsonify({'error': 'Błąd serwera przy sprawdzaniu strefy!'}), 500

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
    zdjecie_path = os.path.join(PHOTOS_DIR, zdjecie_filename)

    try:
        with open(zdjecie_path, 'wb') as zdjecie_file:
            zdjecie_file.write(zdjecie_bytes)
    except IOError as e:
        app.logger.error(f"Błąd przy zapisywaniu zdjęcia: {str(e)}")
        return jsonify({'error': 'Błąd serwera przy zapisywaniu zdjęcia'}), 500

    # Dodanie nowych danych
    new_entry = {
        'id': user_id,
        'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'opis': opis,
        'zdjecie': zdjecie_filename,
        'latitude': latitude,
        'longitude': longitude,
        'kategoria': kategoria
    }

    existing_data.append(new_entry)

    try:
        save_data(DATA_FILE, existing_data)
    except IOError as e:
        app.logger.error(f"Błąd przy zapisywaniu danych: {str(e)}")
        return jsonify({'error': 'Błąd serwera przy zapisywaniu danych'}), 500

    return jsonify({'message': 'Dane zapisane pomyślnie', 'id': user_id}), 200