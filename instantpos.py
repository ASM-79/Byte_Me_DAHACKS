import re
import requests
import math
from datetime import datetime, timedelta

def main():
    # List of Horizons codes and properties for the Sun and planets
    bodies = {
        "Sun": {"code": "10", "mass": 1.989e30, "radius": 696340},
        "Mercury": {"code": "199", "mass": 3.3011e23, "radius": 2439.7},
        "Venus": {"code": "299", "mass": 4.8675e24, "radius": 6051.8},
        "Earth": {"code": "399", "mass": 5.97237e24, "radius": 6371},
        "Mars": {"code": "499", "mass": 6.4171e23, "radius": 3389.5},
        "Jupiter": {"code": "599", "mass": 1.8982e27, "radius": 69911},
    }

    # API URL
    url = "https://ssd.jpl.nasa.gov/api/horizons.api"

    # Get current time and set parameters
    current_time = datetime.now()
    frames = []
    i = 0
    
    while i <= 1:
        start_time = (current_time + timedelta(days=10 * i)).strftime("%Y-%m-%d %H:%M")
        end_time = (current_time + timedelta(days=10 * i + 10)).strftime("%Y-%m-%d %H:%M")
        
        params_template = {
            "format": "text",
            "OBJ_DATA": "NO",
            "MAKE_EPHEM": "YES",
            "EPHEM_TYPE": "OBSERVER",
            "CENTER": "'500@10'",
            "START_TIME": f"'{start_time}'",
            "STOP_TIME": f"'{end_time}'",
            "STEP_SIZE": "'10 d'",
            "QUANTITIES": "'1,20,23'"
        }

        def parse_and_convert(response_text):
            ra_dec_pattern = re.compile(
                r"(\d{4}-\w{3}-\d{2} \d{2}:\d{2})\s+([\d\s.]+)\s+([+\-]\d{2} \d{2} \d{2}\.\d+)\s+([\d.]+)"
            )
            data = []

            for line in response_text.splitlines():
                match = ra_dec_pattern.search(line)
                if match:
                    timestamp, ra, dec, dist = match.groups()

                    # Convert RA from hours, minutes, seconds to decimal degrees
                    ra_parts = [float(part) for part in ra.split()]
                    ra_deg = (ra_parts[0] + ra_parts[1] / 60 + ra_parts[2] / 3600) * 15
                    ra_rad = math.radians(ra_deg)

                    # Convert Dec from degrees, arcminutes, arcseconds to decimal degrees
                    dec_parts = [float(part) for part in dec.split()]
                    dec_deg = dec_parts[0] + dec_parts[1] / 60 + dec_parts[2] / 3600
                    dec_rad = math.radians(dec_deg)

                    # Convert distance from AU to meters (1 AU = 1.496e11 meters)
                    distance_meters = float(dist) * 1.496e11

                    # Calculate Cartesian coordinates in meters
                    x = distance_meters * math.cos(dec_rad) * math.cos(ra_rad)
                    y = distance_meters * math.cos(dec_rad) * math.sin(ra_rad)

                    # Collect coordinates in meters
                    data.append([x, y])

            return data

        # Dictionary to store the final data
        all_data = {}

        # Main loop to fetch data for each body
        for body_name, body_info in bodies.items():
            params = params_template.copy()
            params["COMMAND"] = f"'{body_info['code']}'"
            
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    coords = parse_and_convert(response.text)
                    if coords:
                        latest_coord = coords[-1]
                        all_data[body_name] = [latest_coord[0], latest_coord[1], body_info["mass"], body_info["radius"]]
                else:
                    print(f"Failed to retrieve data for {body_name}: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                print(f"An error occurred while requesting data for {body_name}: {e}")

        frames.append(all_data.items())
        i += 1
        for frame in frames:
            for body_name, (x, y, mass, radius) in frame:
                return (body_name, (x, y, mass, radius))

