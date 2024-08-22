from flask import Blueprint, render_template
import pandas as pd
from utils import load_data, DATA_FILE

table_view_bp = Blueprint('table_view', __name__)

@table_view_bp.route('/table', methods=['GET'])
def table_view():
    data = load_data(DATA_FILE)
    df = pd.DataFrame(data)
    table_html = df.to_html(classes='table table-striped', index=False)
    return render_template('table.html', table_html=table_html)