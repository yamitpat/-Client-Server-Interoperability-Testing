import os
import pytest
import requests
import unittest

BASE_URL = 'http://127.0.0.1:5000/'

#test 1 - check status
def test_status():
    response = requests.get(f"{BASE_URL}/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "uptime" in data["status"]
    assert "processed" in data["status"]
    assert "success" in data["status"]["processed"]
    assert "fail" in data["status"]["processed"]
    assert "health" in data["status"]
    assert data["status"]["health"] in ["ok", "error"]
    assert "api_version" in data["status"]

#test 1 - check status
def test_upload_image_valid():
    image_path = os.path.join(os.path.dirname(__file__), 'assets', 'valid_image.png')
    files = {'image': open(image_path, 'rb')}
    response = requests.post(f"{BASE_URL}/upload_image", files=files)
    files['image'].close()
    assert response.status_code == 200
    data = response.json()
    assert "matches" in data
    assert len(data["matches"]) > 0
    assert "name" in data["matches"][0]
    assert "score" in data["matches"][0]
    assert isinstance(data["matches"][0]["score"], (int, float))


#test 1 - check status
def test_upload_image_invalid_format():
    image_path = os.path.join(os.path.dirname(__file__), 'assets', 'invalid_image.txt')
    files = {'image': open(image_path, 'rb')}
    response = requests.post(f"{BASE_URL}/upload_image", files=files)
    files['image'].close()
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "http_status" in data["error"]
    assert data["error"]["http_status"] == 400
    assert "message" in data["error"]
    assert "Unsupported image format" in data["error"]["message"]

#test 1 - check status
def test_status_after_upload():
    image_path = os.path.join(os.path.dirname(__file__), 'assets', 'valid_image.png')
    files = {'image': open(image_path, 'rb')}
    requests.post(f"{BASE_URL}/upload_image", files=files)
    files['image'].close()

    response = requests.get(f"{BASE_URL}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"]["processed"]["success"] > 0
    assert data["status"]["processed"]["fail"] == 0
