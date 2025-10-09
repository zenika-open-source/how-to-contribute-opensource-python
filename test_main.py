import pytest
from unittest.mock import Mock
from main import app, geocode_city_country

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_geocode_city_country_success(mocker):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {
        "results": [
            {"country": "United Kingdom", "latitude": 51.5074, "longitude": -0.1278},
            {"country": "United States", "latitude": 39.9526, "longitude": -75.1652}
        ]
    }
    mocker.patch('requests.get', return_value=mock_response)

    result = geocode_city_country("London", "United Kingdom")
    assert result == {"latitude": 51.5074, "longitude": -0.1278}

def test_geocode_city_country_not_found(mocker):
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"results": []}
    mocker.patch('requests.get', return_value=mock_response)

    result = geocode_city_country("UnknownCity", "UnknownCountry")
    assert result is None

def test_weather_endpoint_success(client, mocker):
    mocker.patch('main.geocode_city_country', return_value={"latitude": 51.5074, "longitude": -0.1278})

    mock_weather_response = Mock()
    mock_weather_response.ok = True
    mock_weather_response.json.return_value = {"current_weather": {"temperature": 15.0}}
    mocker.patch('requests.get', return_value=mock_weather_response)

    response = client.get('/api/weather?city=London&country=UK')
    assert response.status_code == 200
    assert response.json == {"temperature": 15.0}

def test_weather_endpoint_missing_params(client):
    response = client.get('/api/weather')
    assert response.status_code == 400
    assert response.json == {"error": "City and country are required"}

def test_weather_endpoint_location_not_found(client, mocker):
    mocker.patch('main.geocode_city_country', return_value=None)

    response = client.get('/api/weather?city=Unknown&country=Unknown')
    assert response.status_code == 404
    assert response.json == {"error": "Could not find location. Please try a different city."}

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "Welcome to the PyWeather API!"}