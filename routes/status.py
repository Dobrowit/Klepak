from flask import Blueprint, jsonify
from utils import load_data, get_uptime, DATA_DIR, DATA_FILE, MAX_IMAGE_SIZE
import utils
import os

status_bp = Blueprint('status', __name__)

@status_bp.route('/status', methods=['GET'])
def status():
    #global entry_counter
    #print("endpoint - status - entry_counter:", utils.entry_counter)
    data = load_data(DATA_FILE)
    num_entries = len(data)
    num_images = len([name for name in os.listdir(DATA_DIR) if name.endswith('.jpg') and os.path.isfile(os.path.join(DATA_DIR, name))])

    data_file_size = os.path.getsize(DATA_FILE) if os.path.exists(DATA_FILE) else 0
    images_size = sum(os.path.getsize(os.path.join(DATA_DIR, name)) for name in os.listdir(DATA_DIR) if name.endswith('.jpg') and os.path.isfile(os.path.join(DATA_DIR, name)))

    total_size_mb = round((data_file_size + images_size) / (1024 * 1024), 1)
    data_file_size = round(data_file_size / (1024 * 1024), 1)
    images_size = round(images_size / (1024 * 1024), 1)

    uptime_seconds = int(get_uptime())
    uptime_str = f"{uptime_seconds // 3600}h {uptime_seconds % 3600 // 60}m {uptime_seconds % 60}s"

    status_info = {
        'num_entries': num_entries,
        'num_images': num_images,
        'data_file_size': data_file_size,
        'images_files_size': images_size,
        'total_size_mb': total_size_mb,
        'ip_blocks': utils.ip_blocks,
        'ip_blocks_unknown': utils.ip_blocks_unknown,
        'entry_counter': utils.entry_counter,
        'max_image_size': MAX_IMAGE_SIZE,
        'uptime': uptime_str
    }

    return jsonify(status_info), 200