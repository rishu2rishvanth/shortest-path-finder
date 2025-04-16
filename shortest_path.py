import googlemaps
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from typing import Dict, List, Tuple
import os
from dotenv import load_dotenv
from pathlib import Path

# Step 1: Get the current directory (where this script is located)
base_dir = Path(__file__).resolve().parent
data_dir = base_dir

# Load environment variables
load_dotenv()

# Initialize Google Maps client
API_KEY = os.getenv('API_KEY')
gmaps = googlemaps.Client(key=API_KEY)

# Constants
CACHE_FILE = "cached_distances.json"

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

def fetch_distance(origin: str, dest: str, origin_coords: str, dest_coords: str) -> Tuple[Tuple[str, str], float]:
    """Fetch distance between two landmarks using Google Maps API."""
    try:
        result = gmaps.distance_matrix(origin_coords, dest_coords, mode="driving", units="metric")
        if result["rows"][0]["elements"][0]["status"] == "OK":
            distance_km = result["rows"][0]["elements"][0]["distance"]["value"] / 1000
            return (origin, dest), distance_km
        else:
            print(f"Failed to get distance from {origin} to {dest}.")
            return (origin, dest), float("inf")
    except Exception as e:
        print(f"API Error for {origin} to {dest}: {e}")
        return (origin, dest), float("inf")

def get_distance_matrix(landmarks: Dict[str, str]) -> Dict[Tuple[str, str], float]:
    """Fetch distances in parallel and cache results."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cached_data = json.load(f)
                # Convert string keys back to tuples
                return {tuple(key.split("|")): value for key, value in cached_data.items()}
        except json.JSONDecodeError:
            print("Cache file is corrupted. Deleting and regenerating...")
            os.remove(CACHE_FILE)
        except Exception as e:
            print(f"Error loading cache: {e}. Deleting and regenerating...")
            os.remove(CACHE_FILE)

    distances = {}
    locations = list(landmarks.keys())
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i, origin in enumerate(locations):
            for j, dest in enumerate(locations):
                if i != j:
                    futures.append(
                        executor.submit(
                            fetch_distance, origin, dest, landmarks[origin], landmarks[dest]
                        )
                    )

        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching distances"):
            (origin, dest), distance = future.result()
            distances[(origin, dest)] = distance

    # Convert tuple keys to strings for JSON serialization
    serializable_distances = {f"{origin}|{dest}": distance for (origin, dest), distance in distances.items()}

    # Save distances to cache
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(serializable_distances, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

    return distances
def solve_tsp(locations: List[str], distances: Dict[Tuple[str, str], float]) -> Tuple[List[str], float]:
    """Solve TSP using OR-Tools."""
    def create_distance_callback(dist_matrix):
        """Create a callback to return distances between locations."""
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(dist_matrix[(locations[from_node], locations[to_node])] * 1000)  # Convert to meters

        return distance_callback

    # Create routing index manager
    manager = pywrapcp.RoutingIndexManager(len(locations), 1, 0)

    # Create routing model
    routing = pywrapcp.RoutingModel(manager)

    # Create distance callback
    dist_callback = create_distance_callback(distances)
    transit_callback_index = routing.RegisterTransitCallback(dist_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Set search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)

    # Extract solution
    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            route.append(locations[manager.IndexToNode(index)])
            index = solution.Value(routing.NextVar(index))
        route.append(locations[manager.IndexToNode(index)])  # Return to start
        total_distance = solution.ObjectiveValue() / 1000  # Convert to km
        return route, total_distance
    else:
        print("No solution found.")
        return [], float("inf")

# Main program
if __name__ == "__main__":
    excel_path = data_dir / 'landmarks.xlsx'
    landmarks = read_landmarks(excel_path)
    distances = get_distance_matrix(landmarks)
    locations = list(landmarks.keys())

    # Solve TSP
    shortest_path, shortest_distance = solve_tsp(locations, distances)

    # Display results
    print("\nShortest Path:", " → ".join(shortest_path))
    print(f"Total Distance: {shortest_distance:.2f} km")