import os

from flask import Blueprint, render_template, request, jsonify
from werkzeug.utils import secure_filename
import time
import imghdr

# Blueprint lets us organize routes into different files
# we don't have to put all routes in the "views.py" module
views = Blueprint('views', __name__)
#global veriable
start_time = time.time()
success_count = 0
fail_count = 0

# Define the routes for the views blueprint
@views.route('/')
def home():
    # Return a simple HTML response for the home page
    # 200 is the "OK" HTTP status code
    return render_template('home.html'),200

@views.route('/upload_image', methods=['POST'])
def upload_image():
    global success_count, fail_count

    if 'image' not in request.files:
        fail_count += 1
        return jsonify({"error": {"http_status": 400, "message": "No file selected"}}), 400

    file = request.files['image']
    if file.filename == '':
        fail_count += 1
        return jsonify({"error": {"http_status": 400, "message": "No image selected"}}), 400

    file_type = file.mimetype
    if file_type not in ['image/jpeg', 'image/png']:
        fail_count += 1
        return jsonify({"error": {"http_status": 400, "message": "Unsupported image format"}}), 400

    filename = secure_filename(file.filename)
    upload_folder = 'website/static/uploads'
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    matches = [
        {"name": "cat", "score": 0.91},
        {"name": "dog", "score": 0.07}
    ]

    success_count += 1

    return jsonify({"matches": matches}), 200

@views.route('/about')
def about():
    return render_template('about.html'), 200

@views.route('/status')
def status():
    global success_count, fail_count, start_time
    uptime = round(time.time() - start_time, 1)
    health = "ok"

    response = {
        "status": {
            "uptime": uptime,
            "processed": {
                "success": success_count,
                "fail": fail_count
            },
            "health": health,
            "api_version": 1
        }
    }

    return jsonify(response), 200

@views.route('/secret')
def secret():
    return {"error": {"http_status": 401, "message": "You are not logged in"}}, 401