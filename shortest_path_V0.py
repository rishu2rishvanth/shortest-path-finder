import googlemaps
import itertools  # Importing itertools for permutations
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Google Maps client with your API key
API_KEY = os.getenv('API_KEY')
gmaps = googlemaps.Client(key=API_KEY)

# Landmarks with their coordinates
landmarks = {
    "Hotel Garlica Grand": "14.6794,77.6006",
    "Reliance Digital": "14.6785,77.5997",
    "Neem Tree Hotel": "14.6812,77.6018",
    "KIMS-Saveera Hospital": "14.6778,77.6030",
    "D Mart": "14.6760,77.5975",
}

# Function to calculate distances between all pairs of landmarks
def get_distance_matrix(landmarks):
    distances = {}
    locations = list(landmarks.keys())
    for i in range(len(locations)):
        for j in range(len(locations)):
            if i != j:
                origin = landmarks[locations[i]]
                destination = landmarks[locations[j]]
                result = gmaps.distance_matrix(origin, destination, mode="driving")
                distance_km = result["rows"][0]["elements"][0]["distance"]["value"] / 1000  # Convert meters to km
                distances[(locations[i], locations[j])] = distance_km
    return distances

# Function to calculate the path distance
def calculate_path_distance(path, distances):
    distance = 0
    for i in range(len(path) - 1):
        distance += distances[(path[i], path[i + 1])]
    # Add return to starting point
    distance += distances[(path[-1], path[0])]
    return distance

# Find the shortest path using brute force
def find_shortest_path(locations, distances):
    shortest_distance = float("inf")
    shortest_path = []
    for perm in itertools.permutations(locations):
        distance = calculate_path_distance(perm, distances)
        if distance < shortest_distance:
            shortest_distance = distance
            shortest_path = perm
    return shortest_path, shortest_distance

# Get distances and calculate the shortest path
distances = get_distance_matrix(landmarks)
locations = list(landmarks.keys())
shortest_path, shortest_distance = find_shortest_path(locations, distances)

# Display results
print("Shortest Path:", " -> ".join(shortest_path))
print(f"Total Distance: {shortest_distance:.2f} km")
