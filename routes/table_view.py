from flask import Blueprint, render_template, url_for
import pandas as pd
from utils import load_data, DATA_FILE

table_view_bp = Blueprint('table_view', __name__)

def table_view():
    data = load_data(DATA_FILE)
    df = pd.DataFrame(data)
    
    # Funkcja do tworzenia linku HTML
    def make_clickable(val):
        return f'<a href="{url_for("static", filename="data/" + val)}" target="_blank">{val}</a>'
    
    # Zastosuj funkcję make_clickable do kolumny 'zdjecie'
    df['zdjecie'] = df['zdjecie'].apply(make_clickable)
    
    # Konwertuj DataFrame na HTML z escape=False, aby zachować tagi HTML
    table_html = df.to_html(classes='table table-striped', index=False, escape=False)
    
    return render_template('table.html', table_html=table_html)