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
        "Saturn": {"code": "699", "mass": 5.6834e26, "radius": 58232},
        "Uranus": {"code": "799", "mass": 8.6810e25, "radius": 25362},
        "Neptune": {"code": "899", "mass": 1.02413e26, "radius": 24622}
    }

    # API URL
    url = "https://ssd.jpl.nasa.gov/api/horizons.api"

    # Get current time and set parameters
    current_time = datetime.now()
    frames =[]
    i=0
    while (i<15):
        start_time = (current_time + timedelta(days=i)).strftime("%Y-%m-%d %H:%M")  # Use current time as start time
        end_time = (current_time + timedelta(days=i+1)).strftime("%Y-%m-%d %H:%M")  # Set end time to 1 day from start
        params_template = {
            "format": "text",
            "OBJ_DATA": "NO",
            "MAKE_EPHEM": "YES",
            "EPHEM_TYPE": "OBSERVER",
            "CENTER": "'500@399'",  # Earth as the center (geocentric)
            "START_TIME": f"'{start_time}'",  # Use current time as start time
            "STOP_TIME": f"'{end_time}'",      # Set to 1 day later
            "STEP_SIZE": "'1 d'",               # Time step of 1 day
            "QUANTITIES": "'1,20,23'"
        }
        # Function to parse and convert RA, Dec, and distance into x, y coordinates
        def parse_and_convert(response_text):
            ra_dec_pattern = re.compile(r"(\d{4}-\w{3}-\d{2} \d{2}:\d{2})\s+([\d\s.]+)\s+([+\-]\d{2} \d{2} \d{2}\.\d+)\s+([\d.]+)")
            data = []
            for line in response_text.splitlines():
                match = ra_dec_pattern.search(line)
                if match:
                    _, ra, dec, dist = match.groups()
                    # Convert RA from hours, minutes, seconds to decimal degrees
                    ra_parts = [float(part) for part in ra.split()]
                    ra_deg = (ra_parts[0] + ra_parts[1] / 60 + ra_parts[2] / 3600) * 15  # Convert to degrees
                    ra_rad = math.radians(ra_deg)
                    # Convert Dec from degrees, arcminutes, arcseconds to decimal degrees
                    dec_parts = [float(part) for part in dec.split()]
                    dec_deg = dec_parts[0] + dec_parts[1] / 60 + dec_parts[2] / 3600
                    dec_rad = math.radians(dec_deg)
                    # Convert distance from AU to arbitrary units for scaling
                    distance = float(dist)
                    # Cartesian coordinates before normalization
                    x = distance * math.cos(dec_rad) * math.cos(ra_rad)
                    y = distance * math.cos(dec_rad) * math.sin(ra_rad)
                    # Normalize x and y
                    max_distance = 40  # You can adjust this based on actual distance
                    x_normalized = x / max_distance
                    y_normalized = y / max_distance
                    data.append([x_normalized, y_normalized])  # Collect all matched coordinates
            return data  # Return all matched sets of coordinates
        # Dictionary to store the final data
        all_data = {}
        # Main loop to fetch data for each body
        for body_name, body_info in bodies.items():
            # Update the parameters with the specific body code
            params = params_template.copy()
            params["COMMAND"] = f"'{body_info['code']}'"
            # Request data
            response = requests.get(url, params=params)
            if response.status_code == 200:
                coords = parse_and_convert(response.text)
                if coords:
                    # Get only the latest coordinate (last in the list)
                    latest_coord = coords[-1]  # Last coordinate
                    # Store only values in the list format: [x, y, mass, radius]
                    all_data[body_name] = [latest_coord[0], latest_coord[1], body_info["mass"], body_info["radius"]]
            else:
                print(f"Failed to retrieve data for {body_name}: {response.status_code} - {response.text}")
        # Print the dictionary with values in a formatted way
        frames.append(all_data.items())
        i=i+1
    return frames
if __name__=="__main__":
    main()