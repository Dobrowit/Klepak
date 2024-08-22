import os
import logging
import time
import geoip2.database
from logging.handlers import RotatingFileHandler
from werkzeug.exceptions import Forbidden
from flask import Flask, request
from utils import DATA_DIR, GEOIP_DATABASE, EXEMPT_IPS
import utils

from routes.status import status_bp
from routes.register import register_bp
from routes.upload import upload_bp
from routes.data import data_bp
from routes.map_view import map_view_bp
from routes.table_view import table_view_bp
from routes.help_view import help_view_bp

app = Flask(__name__)

app.register_blueprint(status_bp)
app.register_blueprint(register_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(data_bp)
app.register_blueprint(map_view_bp)
app.register_blueprint(table_view_bp)
app.register_blueprint(help_view_bp)

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
    #global entry_counter
    utils.entry_counter += 1
    print(utils.entry_counter)
    app.logger.info(f"Mamy gościa - Adres IP: {request.remote_addr}, URL: {request.url}, Metoda: {request.method}, User-Agent: {request.user_agent}")

# Blokowanie wejść spoza Polski
@app.before_request
def block_non_polish_ips():
    global IP_BLOCKS, IP_BLOCKS_UNKNOWN

    if request.remote_addr in EXEMPT_IPS:
        app.logger.info(f"Adres IP: {request.remote_addr} znajduje się na liście wyjątków, dostęp przyznany.")
        return  # Przejdź dalej bez blokowania
    try:
        response = geoip_reader.country(request.remote_addr)
        if response.country.iso_code != 'PL':
            app.logger.warning(f"Blokowane połączenie z adresu IP: {request.remote_addr} (kraj: {response.country.iso_code})")
            IP_BLOCKS += 1
            raise Forbidden(description="Dostęp zabroniony: połączenia spoza Polski są blokowane.")
    except geoip2.errors.AddressNotFoundError:
        app.logger.warning(f"Nieznany adres IP: {request.remote_addr}. Blokowanie połączenia.")
        IP_BLOCKS_UNKNOWN += 1
        raise Forbidden(description="Dostęp zabroniony: nieznany adres IP.")
    
if __name__ == '__main__':
    app.run(debug=True, port=20162)
