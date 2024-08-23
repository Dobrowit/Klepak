from flask import Blueprint, request, render_template, url_for
from utils import load_data, DATA_FILE
import folium
from folium.plugins import MarkerCluster

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

    # Utworzenie mapy
    map_ = folium.Map(location=[54.7578, 17.5610], zoom_start=15)

    # Dodanie MarkerCluster do mapy
    marker_cluster = MarkerCluster(icon_create_function="""
        function(cluster) {
            return L.divIcon({ 
                html: '<div style="background-color:red;"><span>' + cluster.getChildCount() + '</span></div>', 
                className: 'marker-cluster', 
                iconSize: new L.Point(40, 40) 
            });
        }
    """).add_to(map_)

    for entry in data:
        popup_content = f"""
<div>
    <img src="{url_for('static', filename='photos/' + entry['zdjecie'])}" style="max-width:100px; max-height:100px;">
    <p>{entry['data']}: {entry['opis']}</p>
</div>
"""
        folium.Marker(
            location=[entry['latitude'], entry['longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=entry['opis'],
            icon=folium.Icon(color='red', icon='info-sign')  # Ustawienie czerwonego koloru markera
        ).add_to(marker_cluster)

    map_html = map_._repr_html_()
    return render_template('map.html', map_html=map_html)