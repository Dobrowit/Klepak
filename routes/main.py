from flask import Blueprint, render_template, url_for
import pandas as pd
from utils import load_data, DATA_FILE, CATEGORY_FILE

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return redirect(url_for('map_view'))
