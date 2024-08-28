from flask import Blueprint, url_for, redirect

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return redirect(url_for('table_view.table_view'))
