import googlemaps
import pandas as pd
from itertools import permutations
from typing import Dict, Tuple, List
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Google Maps client
API_KEY = os.getenv('API_KEY')
gmaps = googlemaps.Client(key=API_KEY)

def read_landmarks(file_path: str) -> Dict[str, str]:
    """Read landmarks from Excel with validation."""
    try:
        df = pd.read_excel(file_path)
        required_columns = ["Landmark Name", "Latitude", "Longitude"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Missing required columns in Excel file.")
        return {row['Landmark Name']: f"{row['Latitude']},{row['Longitude']}" for _, row in df.iterrows()}
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit()

def get_distance_matrix(landmarks: Dict[str, str]) -> Dict[Tuple[str, str], float]:
    """Fetch distances with API error handling."""
    distances = {}
    locations = list(landmarks.keys())
    for i, origin in enumerate(locations):
        for j, dest in enumerate(locations):
            if i != j:
                try:
                    result = gmaps.distance_matrix(
                        landmarks[origin], 
                        landmarks[dest], 
                        mode="driving",
                        units="metric"
                    )
                    if result["rows"][0]["elements"][0]["status"] == "OK":
                        distance_km = result["rows"][0]["elements"][0]["distance"]["value"] / 1000
                        distances[(origin, dest)] = distance_km
                    else:
                        print(f"Failed to get distance from {origin} to {dest}.")
                except Exception as e:
                    print(f"API Error: {e}")
    return distances

def calculate_path_distance(path: List[str], distances: Dict[Tuple[str, str], float]) -> float:
    """Calculate total path distance."""
    total = 0.0
    for i in range(len(path) - 1):
        total += distances.get((path[i], path[i + 1]), float("inf"))
    # Optional: Add return to start
    # total += distances.get((path[-1], path[0]), float("inf"))
    return total

def find_shortest_path(locations: List[str], distances: Dict[Tuple[str, str], float]) -> Tuple[List[str], float]:
    """Find shortest path using permutations (for small n)."""
    if len(locations) > 10:
        print("Warning: Brute-force is impractical for n > 10.")
        return [], float("inf")
    
    shortest_distance = float("inf")
    shortest_path = []
    for perm in permutations(locations):
        current_distance = calculate_path_distance(perm, distances)
        if current_distance < shortest_distance:
            shortest_distance = current_distance
            shortest_path = perm
    return shortest_path, shortest_distance

# Example usage
if __name__ == "__main__":
    excel_path = r"D:\website\shortest-path\landmarks.xlsx"
    landmarks = read_landmarks(excel_path)
    distances = get_distance_matrix(landmarks)
    locations = list(landmarks.keys())
    
    start_time = time.time()
    shortest_path, shortest_distance = find_shortest_path(locations, distances)
    print(f"Execution time: {time.time() - start_time:.2f} seconds")
    
    print("\nShortest Path:", " → ".join(shortest_path))
    print(f"Total Distance: {shortest_distance:.2f} km")