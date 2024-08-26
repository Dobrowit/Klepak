from flask import Blueprint, request, render_template, url_for, jsonify
from utils import load_data, DATA_FILE, CATEGORY_FILE
import folium

item_view_bp = Blueprint('map_view', __name__)

@item_view_bp.route('/item', methods=['GET'])
def map_view():
    entry_id = request.args.get('id')
    data = load_data(DATA_FILE)
    kategorie = load_data(CATEGORY_FILE)

    if entry_id:
        data = [entry for entry in data if str(entry['id']) == str(entry_id)]
        if not data:
            return jsonify({'error': 'Nie znaleziono danych dla podanego ID'}), 404
    else:
        data = [{k: v for k, v in entry.items() if k != 'id'} for entry in data]

    kat_id = data['kategoria']

    # Znalezienie kategorii na podstawie kat_id
    category = next((category for category in kategorie if category['id'] == kat_id), None)
    if category:
        nazwa_kat = category['nazwa_kat']
        icon_symbol = category['ikona']

    # Utworzenie mapy
    map_ = folium.Map(location=[54.7578, 17.5610], zoom_start=15)

    item_ = f"""
<div>
    <img src="{url_for('static', filename='photos/' + data['zdjecie'])}" style="max-width:300px; max-height:200px;">
    <h1>{nazwa_kat}</h1>
    <p>{data['data']}</p>
    <hr style="border: 3px solid black; margin: 0;">
    <p>{data['opis']}</p>
</div>
"""
    folium.Marker(
        location = [data['latitude'], data['longitude']],
        icon = folium.Icon(color = 'red',
                            icon = icon_symbol,
                            prefix = 'fa')).add_to(map_)

    item_html = item_._repr_html_()
    return render_template('item.html', item_html=item_html)