import pytest
import requests

@pytest.fixture
def base_url():
    return "http://localhost:8080"

def test_get_weather(base_url):
    url = f"{base_url}/api/weather?city=London&country=Uk"
    response = requests.get(url)

    assert response.status_code == 200
    data = response.json()

    assert "latitude" in data
    assert "longitude" in data
