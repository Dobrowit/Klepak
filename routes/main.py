from flask import Blueprint, url_for, redirect
import pandas as pd

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return redirect(url_for('map_view'))
