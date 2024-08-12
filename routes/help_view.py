from flask import Blueprint, render_template

help_view_bp = Blueprint('help_view', __name__)

@help_view_bp.route('/help', methods=['GET'])
def help_view():
    return render_template('help.html')