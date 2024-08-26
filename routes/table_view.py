from flask import Blueprint, jsonify
from utils import load_data, DATA_FILE

item_view_bp = Blueprint('item_view', __name__)

@item_view_bp.route('/data', methods=['GET'])
def get_data():
    data = load_data(DATA_FILE)
    # Filtracja danych i usunięcie niepotrzebnych kolumn
    filtered_data = [
        {
            'id': entry['id'],
            'data': entry['data'],
            'opis': entry['opis'],
            'zdjecie': entry['zdjecie']
        }
        for entry in data
    ]
    return jsonify(filtered_data)
