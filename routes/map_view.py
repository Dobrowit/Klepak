from flask import Blueprint, render_template
from utils import load_data
import folium

map_view_bp = Blueprint('map_view', __name__)

@map_view_bp.route('/map', methods=['GET'])
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