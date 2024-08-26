from flask import Blueprint, request, jsonify
from utils import load_data, CATEGORY_FILE

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    entry_id = request.args.get('id')
    data = load_data(CATEGORY_FILE)

    if entry_id:
        # Konwersja entry_id na int
        try:
            entry_id = int(entry_id)
        except ValueError:
            return jsonify({'error': 'Niepoprawny format ID'}), 400

        data = [entry for entry in data if entry['id'] == entry_id]
        if not data:
            return jsonify({'error': 'Nie znaleziono danych dla podanego ID'}), 404
    # Jeśli brak parametru id, zwracamy wszystkie dane
    else:
        return jsonify(data), 200

    return jsonify(data), 200

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    categories = load_data(CATEGORY_FILE)
    category = next((cat for cat in categories if cat['id'] == category_id), None)
    
    if category is None:
        return jsonify({'error': 'Nie znaleziono kategorii o podanym ID'}), 404
    
    return jsonify(category), 200
