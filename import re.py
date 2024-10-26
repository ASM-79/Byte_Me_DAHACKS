import re
import requests
import math
from datetime import datetime, timedelta
import json

def main(i, j):
    bodies = {
        "Sun": {"code": "10", "mass": 1.989e30, "radius": 696340},
        "Mercury": {"code": "199", "mass": 3.3011e23, "radius": 2439.7},
        "Venus": {"code": "299", "mass": 4.8675e24, "radius": 6051.8},
        "Earth": {"code": "399", "mass": 5.97237e24, "radius": 6371},
        "Mars": {"code": "499", "mass": 6.4171e23, "radius": 3389.5},
        "Jupiter": {"code": "599", "mass": 1.8982e27, "radius": 69911}
    }

    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    current_time = datetime.now()
    frames = []
    
    for i in range(i, j):
        start_time = (current_time + timedelta(days=10 * i)).strftime("%Y-%m-%d %H:%M")
        end_time = (current_time + timedelta(days=10 * i + 10)).strftime("%Y-%m-%d %H:%M")
        
        params_template = {
            "format": "text",
            "OBJ_DATA": "NO",
            "MAKE_EPHEM": "YES",
            "EPHEM_TYPE": "OBSERVER",
            "CENTER": "'10'",
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

                    ra_parts = [float(part) for part in ra.split()]
                    ra_deg = (ra_parts[0] + ra_parts[1] / 60 + ra_parts[2] / 3600) * 15
                    ra_rad = math.radians(ra_deg)

                    dec_parts = [float(part) for part in dec.split()]
                    dec_deg = dec_parts[0] + dec_parts[1] / 60 + dec_parts[2] / 3600
                    dec_rad = math.radians(dec_deg)

                    distance = float(dist)

                    x = distance * math.cos(dec_rad) * math.cos(ra_rad)
                    y = distance * math.cos(dec_rad) * math.sin(ra_rad)

                    max_distance = 40
                    x_normalized = x / max_distance
                    y_normalized = y / max_distance

                    data.append([x_normalized, y_normalized])

            return data

        all_data = {}

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

        frames.append(all_data)

    return frames

frames = []
frames.extend(main(0, 35))
frames.extend(main(36, 72))

with open("data.txt", "a") as data:
    for frame in frames:
        print(frame)
        data.write(json.dumps(frame, indent=2) + "\n")
