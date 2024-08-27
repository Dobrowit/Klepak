import os
import logging
import time
import geoip2.database
from logging.handlers import RotatingFileHandler
from werkzeug.exceptions import Forbidden
from flask import Flask, request, send_from_directory, redirect, url_for
from utils import DATA_DIR, GEOIP_DATABASE, EXEMPT_IPS
import utils

from routes.status import status_bp
from routes.register import register_bp
from routes.upload import upload_bp
from routes.data import data_bp
from routes.map_view import map_view_bp
from routes.table_view import table_view_bp
from routes.help_view import help_view_bp
from routes.categories import categories_bp
from routes.item_view import item_view_bp

app = Flask(__name__)

app.register_blueprint(status_bp)
app.register_blueprint(register_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(data_bp)
app.register_blueprint(map_view_bp)
app.register_blueprint(table_view_bp)
app.register_blueprint(help_view_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(item_view_bp)

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if not os.path.exists('logs'):
    os.mkdir('logs')

if not os.path.exists(GEOIP_DATABASE):
    raise FileNotFoundError("Brak pliku bazy danych GeoIP. Upewnij się, że plik GeoLite2-Country.mmdb jest dostępny.")

# Dziennik
file_handler = RotatingFileHandler('logs/klepak.log', maxBytes=102400, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Klepak startup')

# Ładowanie bazy GeoIP
geoip_reader = geoip2.database.Reader(GEOIP_DATABASE)
app.logger.info(f"Baza GeoIP załadowana")

# Logowanie adresów IP
@app.before_request
def log_request_info():
    user_agent_string = request.user_agent.string 
    if "Uptime-Kuma" in user_agent_string:
        pass
    else:
        utils.entry_counter += 1
        app.logger.info(f"Mamy gościa - Adres IP: {request.remote_addr}, URL: {request.url}, Metoda: {request.method}, User-Agent: {user_agent_string}")

# Blokowanie wejść spoza Polski
@app.before_request
def block_non_polish_ips():
    if request.remote_addr in EXEMPT_IPS:
        app.logger.info(f"Adres IP: {request.remote_addr} znajduje się na liście wyjątków, dostęp przyznany.")
        return  # Przejdź dalej bez blokowania
    try:
        response = geoip_reader.country(request.remote_addr)
        if response.country.iso_code not in ['PL', 'FI']:
            app.logger.warning(f"Blokowane połączenie z adresu IP: {request.remote_addr} (kraj: {response.country.iso_code})")
            utils.ip_blocks += 1
            raise Forbidden(description="Dostęp zabroniony: połączenia spoza Polski są blokowane.")
    except geoip2.errors.AddressNotFoundError:
        app.logger.warning(f"Nieznany adres IP: {request.remote_addr}. Blokowanie połączenia.")
        utils.ip_blocks_unknown += 1
        raise Forbidden(description="Dostęp zabroniony: nieznany adres IP.")

# Manifest PWA - SPRAWDZIĆ CZY DZIAŁA!!!!
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('', 'service-worker.js')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        directory=app.static_folder,
        path='favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

main_bp = Blueprint('main', __name__)
app.register_blueprint(main_bp)

@app.route('/')
def home():
    return redirect(url_for('map_view'))

if __name__ == '__main__':
    app.run(debug=True, port=20162)
