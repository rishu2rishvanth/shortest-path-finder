import os
import googlemaps
import itertools
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    raise ValueError("API_KEY not found in environment variables.")

# Initialize Google Maps Client
gmaps = googlemaps.Client(key=API_KEY)

# Define landmarks and coordinates here or read from Excel/JSON
landmarks = {
    "Hotel Garlica Grand": "14.6794,77.6006",
    "Reliance Digital": "14.6785,77.5997",
    "Neem Tree Hotel": "14.6812,77.6018",
    "KIMS-Saveera Hospital": "14.6778,77.6030",
    "D Mart": "14.6760,77.5975",
}

def get_distance_matrix(landmarks):
    """Fetch pairwise distances using Google Maps API"""
    distances = {}
    locations = list(landmarks.keys())
    for i in range(len(locations)):
        for j in range(len(locations)):
            if i != j:
                origin = landmarks[locations[i]]
                destination = landmarks[locations[j]]
                try:
                    result = gmaps.distance_matrix(origin, destination, mode="driving")
                    if result["rows"][0]["elements"][0]["status"] == "OK":
                        distance_km = result["rows"][0]["elements"][0]["distance"]["value"] / 1000
                    else:
                        print(f"Error getting distance from {locations[i]} to {locations[j]}")
                        distance_km = float("inf")
                except Exception as e:
                    print(f"API Error: {e}")
                    distance_km = float("inf")
                distances[(locations[i], locations[j])] = distance_km
    return distances

def calculate_path_distance(path, distances):
    """Calculate total path distance including return to start"""
    total = 0
    for i in range(len(path) - 1):
        total += distances[(path[i], path[i + 1])]
    total += distances[(path[-1], path[0])]  # Return to starting point
    return total

def find_shortest_path(locations, distances):
    """Find the shortest path using brute-force permutation"""
    shortest_distance = float("inf")
    shortest_path = []
    for perm in itertools.permutations(locations):
        distance = calculate_path_distance(perm, distances)
        if distance < shortest_distance:
            shortest_distance = distance
            shortest_path = perm
    return shortest_path, shortest_distance

if __name__ == "__main__":
    distances = get_distance_matrix(landmarks)
    locations = list(landmarks.keys())
    shortest_path, shortest_distance = find_shortest_path(locations, distances)

    print("\nShortest Path:", " → ".join(shortest_path))
    print(f"Total Distance: {shortest_distance:.2f} km")
