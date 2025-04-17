import os
import googlemaps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Google Maps client with the API key
API_KEY = os.getenv('API_KEY')
gmaps = googlemaps.Client(key=API_KEY)

# Test API by getting geolocation of a known place (e.g., Google headquarters)
def test_api_connection():
    try:
        geocode_result = gmaps.geocode("1600 Amphitheatre Parkway, Mountain View, CA")
        if geocode_result:
            print("API connection successful! Geocode result:")
            print(geocode_result)
        else:
            print("API connection successful, but no results found.")
    except Exception as e:
        print(f"API connection failed: {e}")

if __name__ == "__main__":
    test_api_connection()
