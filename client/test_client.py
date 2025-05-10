import os
import pytest
import requests


BASE_URL = 'http://127.0.0.1:5000/'


@pytest.mark.parametrize("filename,mime_type,expected_code", [
    ("cat.jpeg", "image/jpeg", 200),
    ("corrupted.jpg", "image/jpeg", 400),
    ("empty.jpg", "image/jpeg", 400),
])
# Parametrized tests for various input types: valid, corrupted, empty
def test_upload_various_files(filename, mime_type, expected_code):
    path = os.path.join("client", "assets", filename)
    with open(path, "rb") as f:
        files = {"image": (filename, f, mime_type)}
        res = requests.post(f"{BASE_URL}/upload_image", files=files)
        assert res.status_code == expected_code

# Test to check status
def test_status():
    res = requests.get(f"{BASE_URL}/status")
    assert res.status_code == 200
    assert "uptime" in res.json()["status"]

# Test valid PNG upload
def test_upload_image_valid():
    with open("client/assets/valid_image.png", "rb") as f:
        files = {"image": ("valid_image.png", f, "image/png")}
        res = requests.post(f"{BASE_URL}/upload_image", files=files)
        assert res.status_code == 200
        assert "matches" in res.json()


# Test upload of unsupported MIME type
def test_upload_image_invalid_format():
    with open("client/assets/invalid_image.txt", "rb") as f:
        files = {"image": ("invalid_image.txt", f, "text/plain")}
        res = requests.post(f"{BASE_URL}/upload_image", files=files)
        assert res.status_code == 400
        assert "error" in res.json()


# Test rejection if Content-Type is incorrect despite valid file
def test_wrong_content_type_with_valid_image():
    with open("client/assets/valid_image.png", "rb") as f:
        files = {"image": ("valid_image.png", f, "application/octet-stream")}
        res = requests.post(f"{BASE_URL}/upload_image", files=files)
        assert res.status_code == 400

# Test rejection of GET on a POST-only endpoint
def test_get_upload_image():
    res = requests.get(f"{BASE_URL}/upload_image")
    assert res.status_code == 405

# Test upload with no 'image' field
def test_missing_image_key():
    res = requests.post(f"{BASE_URL}/upload_image", files={})
    assert res.status_code == 400


def get_status_counts():
    # ensures successful image upload increases the success count
    res = requests.get(f"{BASE_URL}/status")
    assert res.status_code == 200
    stats = res.json()["status"]["processed"]
    return stats["success"], stats["fail"]

# Test status counter increases on valid upload
def test_status_increments_on_success():
    # ensures invalid upload increases the failure count
    success_before, fail_before = get_status_counts()

    with open("client/assets/valid_image.png", "rb") as f:
        files = {"image": ("valid_image.png", f, "image/png")}
        res = requests.post(f"{BASE_URL}/upload_image", files=files)
        assert res.status_code == 200

    success_after, fail_after = get_status_counts()
    assert success_after == success_before + 1
    assert fail_after == fail_before

# Test status counter increases on invalid upload
def test_status_increments_on_failure():
    success_before, fail_before = get_status_counts()

    with open("client/assets/invalid_image.txt", "rb") as f:
        files = {"image": ("invalid_image.txt", f, "text/plain")}
        res = requests.post(f"{BASE_URL}/upload_image", files=files)
        assert res.status_code == 400

    success_after, fail_after = get_status_counts()
    assert fail_after == fail_before + 1
    assert success_after == success_before

