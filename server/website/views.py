import time
from flask import Blueprint, render_template, request, jsonify
from PIL import Image
from io import BytesIO
import requests
from dotenv import load_dotenv
import os


# Blueprint lets us organize routes into different files
# we don't have to put all routes in the "views.py" module
views = Blueprint('views', __name__)

#global variable
start_time = time.time()
success_count = 0
fail_count = 0

# Hugging Face API endpoint for image classification
HF_API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"

# API token for authentication
load_dotenv()
HF_API_TOKEN =os.getenv("HF_API_TOKEN")
def call_image_classification_api(image_bytes):
    # Detect image format to set correct Content-Type
    # Send image to Hugging Face inference API
    try:
        img = Image.open(BytesIO(image_bytes))
        format_to_mime = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "JPG": "image/jpeg"
        }
        mime_type = format_to_mime.get(img.format)
        if not mime_type:
            raise Exception(f"Unsupported image format: {img.format}")
    except Exception:
        raise Exception("Could not determine image format")

    # Fallback if no token is set
    if not HF_API_TOKEN:
        print("[INFO] No HF_API_TOKEN found. Using fallback mock classification.")
        return [
            {"name": "fallback_object", "score": 1.0}
        ]

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": mime_type
    }
    response = requests.post(HF_API_URL, headers=headers, data=image_bytes)

    if response.status_code != 200:
        raise Exception("External API error")

    results = response.json()

    # Convert Hugging Face response to your required format
    matches = []
    total_score = sum(r["score"] for r in results)
    for r in results:
        matches.append({
            "name": r["label"],
            "score": round(r["score"] / total_score, 3)  # normalize
        })

    return matches
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

    if file.mimetype not in ['image/jpeg', 'image/png']:
        fail_count += 1
        return jsonify({"error": {"http_status": 400, "message": "Unsupported image format"}}), 400
    # Validate and decode image using Pillow
    try:
        image_bytes = file.read()

        #Check if it's a valid image
        img = Image.open(BytesIO(image_bytes))
        img.verify()

        # If valid, send to external API and format respons
        matches = call_image_classification_api(image_bytes)

        success_count += 1
        return jsonify({"matches": matches})
    except Exception as e:
        fail_count += 1
        return jsonify({"error": {"http_status": 400, "message": str(e)}}), 400

def method_not_allowed(e):
    return jsonify({"error": {"http_status": 405, "message": "Method not allowed"}}), 405

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

@views.route('/secret')     # TODO: maybe need to erase this?
def secret():
    return {"error": {"http_status": 401, "message": "You are not logged in"}}, 401