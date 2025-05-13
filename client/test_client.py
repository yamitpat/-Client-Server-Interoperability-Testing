import os
import pytest
import requests
from flask import Flask
from server.website.views import views 


@pytest.fixture 
def app(): 
    app = Flask(__name__) 
    app.register_blueprint(views) 
    return app 

@pytest.fixture
def client(app):
    return app.test_client()

# # Parametrized tests for various input types: valid, corrupted, empty
@pytest.mark.parametrize("filename,mime_type,expected_code", [
    ("cat.jpeg", "image/jpeg", 200),
    ("corrupted.jpg", "image/jpeg", 400),
    ("empty.jpg", "image/jpeg", 400),
])
def test_upload_various_files(client, filename, mime_type, expected_code):
    path = os.path.join("client", "assets", filename)
    with open(path, "rb") as f:
        data = {"image": (f, filename)}
        res = client.post("/upload_image", data=data, content_type='multipart/form-data')
        assert res.status_code == expected_code

# Test to check status
def test_status(client):
    res = client.get(f"/status")
    assert res.status_code == 200
    assert "uptime" in res.json["status"]

# Test valid PNG upload
def test_upload_image_valid(client):
    with open("client/assets/valid_image.png", "rb") as f:
        data = {"image": (f, "valid_image.png")}
        res = client.post("/upload_image", data=data, content_type='multipart/form-data')
        assert res.status_code == 200
        assert "matches" in res.json


# Test upload of unsupported MIME type
def test_upload_image_invalid_format(client):
    with open("client/assets/invalid_image.txt", "rb") as f:
        data = {"image": (f, "invalid_image.txt")}
        res = client.post("/upload_image", data=data, content_type='multipart/form-data')
        assert res.status_code == 400
        assert "error" in res.json


# Test rejection if Content-Type is incorrect despite valid file
def test_wrong_content_type_with_valid_image(client):
    with open("client/assets/valid_image.png", "rb") as f:
        data = {"image": (f, "valid_image.png")}
        res = client.post("/upload_image", data=data, content_type='application/octet-stream')
        assert res.status_code == 400

# Test rejection of GET on a POST-only endpoint
def test_get_upload_image(client):
    res = client.get("/upload_image")
    assert res.status_code == 405

# Test upload with no 'image' field
def test_missing_image_key(client):
    res = client.post("/upload_image", data={}, content_type='multipart/form-data')
    assert res.status_code == 400


def get_status_counts(client):
    # ensures successful image upload increases the success count
    res = client.get("/status")
    assert res.status_code == 200
    stats = res.json["status"]["processed"]
    return stats["success"], stats["fail"]

# Test status counter increases on valid upload
def test_status_increments_on_success(client):
    # ensures invalid upload increases the failure count
    success_before, fail_before = get_status_counts(client)

    with open("client/assets/valid_image.png", "rb") as f:
        data = {"image": (f, "valid_image.png")}
        res = client.post("/upload_image", data=data, content_type='multipart/form-data')
        assert res.status_code == 200

    success_after, fail_after = get_status_counts(client)
    assert success_after == success_before + 1
    assert fail_after == fail_before

# Test status counter increases on invalid upload
def test_status_increments_on_failure(client):
    success_before, fail_before = get_status_counts(client)

    with open("client/assets/invalid_image.txt", "rb") as f:
        data = {"image": (f, "invalid_image.txt")}
        res = client.post("/upload_image", data=data, content_type='multipart/form-data')
        assert res.status_code == 400

    success_after, fail_after = get_status_counts(client)
    assert fail_after == fail_before + 1
    assert success_after == success_before

