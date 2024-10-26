import re
import requests
import math
from datetime import datetime, timedelta

def main(i,j):
    # List of Horizons codes and properties for the Sun and planets
    bodies = {
        "Sun": {"code": "10", "mass": 1.989e30, "radius": 696340},
        "Mercury": {"code": "199", "mass": 3.3011e23, "radius": 2439.7},
        "Venus": {"code": "299", "mass": 4.8675e24, "radius": 6051.8},
        "Earth": {"code": "399", "mass": 5.97237e24, "radius": 6371},
        "Mars": {"code": "499", "mass": 6.4171e23, "radius": 3389.5},
        "Jupiter": {"code": "599", "mass": 1.8982e27, "radius": 69911},
        #"Saturn": {"code": "699", "mass": 5.6834e26, "radius": 58232},
        #"Uranus": {"code": "799", "mass": 8.6810e25, "radius": 25362},
        #"Neptune": {"code": "899", "mass": 1.02413e26, "radius": 24622},
        #"Pluto": {"code": "901", "mass": 1.303e22, "radius": 1188.3},
    }

    # API URL
    url = "https://ssd.jpl.nasa.gov/api/horizons.api"

    # Get current time and set parameters
    current_time = datetime.now()
    frames = []
    
    for i in range (i,j):
        start_time = (current_time + timedelta(days=10 * i)).strftime("%Y-%m-%d %H:%M")  # Use current time as start time
        end_time = (current_time + timedelta(days=10 * i + 10)).strftime("%Y-%m-%d %H:%M")  # Set end time to 10 days later
        
        params_template = {
            "format": "text",
            "OBJ_DATA": "NO",
            "MAKE_EPHEM": "YES",
            "EPHEM_TYPE": "OBSERVER",
            "CENTER": "'10'",  # Heliocentric system centered on the Sun
            "START_TIME": f"'{start_time}'",  # Use current time as start time
            "STOP_TIME": f"'{end_time}'",      # Set to 10 days later
            "STEP_SIZE": "'10 d'",               # Time step of 10 days
            "QUANTITIES": "'1,20,23'"
        }

        # Function to parse and convert RA, Dec, and distance into x, y coordinates
        def parse_and_convert(response_text):
            # Regex pattern to match the expected line format
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
                    ra_deg = (ra_parts[0] + ra_parts[1] / 60 + ra_parts[2] / 3600) * 15  # Convert to degrees
                    ra_rad = math.radians(ra_deg)

                    # Convert Dec from degrees, arcminutes, arcseconds to decimal degrees
                    dec_parts = [float(part) for part in dec.split()]
                    dec_deg = dec_parts[0] + dec_parts[1] / 60 + dec_parts[2] / 3600
                    dec_rad = math.radians(dec_deg)

                    # Convert distance from AU to float
                    distance = float(dist)

                    # Calculate Cartesian coordinates relative to the Sun
                    x = distance * math.cos(dec_rad) * math.cos(ra_rad)
                    y = distance * math.cos(dec_rad) * math.sin(ra_rad)

                    # Normalize x and y
                    max_distance = 40  # Adjust this based on actual distance
                    x_normalized = x / max_distance
                    y_normalized = y / max_distance

                    # Collect normalized coordinates
                    data.append([x_normalized, y_normalized])

            return data  # Return all matched sets of coordinates

        # Dictionary to store the final data
        all_data = {}

        # Main loop to fetch data for each body
        for body_name, body_info in bodies.items():
            # Update the parameters with the specific body code
            params = params_template.copy()
            params["COMMAND"] = f"'{body_info['code']}'"
            # Request data
            try:
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
            except requests.RequestException as e:
                print(f"An error occurred while requesting data for {body_name}: {e}")

        frames.append(all_data.items())

    return frames
frames=main(0,35)
frames.append(main(36,72))
frames
data=open("data.txt","a")
for frame in frames():
    print (frame)
    data.write(str(frame))
data.close()



