from flask import Blueprint, request, jsonify
from utils import load_data, save_data, validate_email, validate_phone, USERS_FILE
import uuid, time, os

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['POST'])
def register():
    content = request.json
    imie = content.get('imie')
    nazwisko = content.get('nazwisko')
    email = content.get('email')
    phone = content.get('phone')

    if not all([email, phone]):
        return jsonify({'error': 'Brakuje jednego z wymaganych pól: email, phone'}), 400

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