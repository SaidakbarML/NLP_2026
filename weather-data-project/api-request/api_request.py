import requests
api_url = "http://api.weatherstack.com/current?access_key=1aef22cdaf6a64576892902a0729b5c5&query=New York"
def fetch_data():
    print('fetching data from server')
    try:
        responce = requests.get(api_url)
        responce.raise_for_status()
        return responce.json()
    except requests.exceptions.RequestException as e:
        print(f'an error occured {e}')
        raise

def mock_fetch():
    return {'request': {'type': 'City', 'query': 'New York, United States of America', 'language': 'en', 'unit': 'm'}, 'location': {'name': 'New York', 'country': 'United States of America', 'region': 'New York', 'lat': '40.714', 'lon': '-74.006', 'timezone_id': 'America/New_York', 'localtime': '2026-02-24 11:33', 'localtime_epoch': 1771932780, 'utc_offset': '-5.0'}, 'current': {'observation_time': '04:33 PM', 'temperature': -3, 'weather_code': 116, 'weather_icons': ['https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0002_sunny_intervals.png'], 'weather_descriptions': ['Partly Cloudy '], 'astro': {'sunrise': '06:37 AM', 'sunset': '05:42 PM', 'moonrise': '10:15 AM', 'moonset': '01:13 AM', 'moon_phase': 'First Quarter', 'moon_illumination': 44}, 'air_quality': {'co': '288.85', 'no2': '15.55', 'o3': '73', 'so2': '4.05', 'pm2_5': '8.35', 'pm10': '8.75', 'us-epa-index': '1', 'gb-defra-index': '1'}, 'wind_speed': 24, 'wind_degree': 305, 'wind_dir': 'NW', 'pressure': 1013, 'precip': 0, 'humidity': 50, 'cloudcover': 0, 'feelslike': -9, 'uv_index': 3, 'visibility': 13, 'is_day': 'yes'}}

