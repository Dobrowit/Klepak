from flask import Blueprint, request, jsonify
from utils import load_data, DATA_FILE, CATEGORY_FILE

data_bp = Blueprint('data', __name__)

@data_bp.route('/data', methods=['GET'])
def get_data():
    entry_id = request.args.get('id')
    data = load_data(DATA_FILE)
    categories = load_data(CATEGORY_FILE)

    # Tworzenie słownika kategorii dla szybkiego wyszukiwania
    category_dict = {cat['id']: cat['nazwa_kat'] for cat in categories}

    # Dodawanie nazwy kategorii do każdego wpisu
    for entry in data:
        entry['nazwa_kat'] = category_dict.get(entry.get('kategoria'), 'Nieznana kategoria')

    if entry_id:
        data = [entry for entry in data if str(entry['id']) == str(entry_id)]
        if not data:
            return jsonify({'error': 'Nie znaleziono danych dla podanego ID'}), 404
    # else:
    #     data = [{k: v for k, v in entry.items() if k != 'id'} for entry in data]

    return jsonify(data), 200
