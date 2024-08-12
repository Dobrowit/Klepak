from flask import Blueprint, request, jsonify
from utils import load_data

data_bp = Blueprint('data', __name__)

@data_bp.route('/data', methods=['GET'])
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