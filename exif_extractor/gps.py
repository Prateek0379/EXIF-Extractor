import folium
from typing import List, Dict


def generate_map(metadata_list: List[Dict], output_path: str = "map.html"):
    """Generate an interactive Folium map from GPS-tagged images."""
    gps_entries = [
        m for m in metadata_list
        if m.get("gps", {}).get("available")
    ]

    if not gps_entries:
        print("No GPS data found in any images.")
        return None

    # Centre map on mean coordinates
    avg_lat = sum(m["gps"]["latitude"] for m in gps_entries) / len(gps_entries)
    avg_lon = sum(m["gps"]["longitude"] for m in gps_entries) / len(gps_entries)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12, tiles="OpenStreetMap")

    for entry in gps_entries:
        gps = entry["gps"]
        cam = entry.get("camera", {})
        ts = entry.get("timestamps", {})
        popup_html = f"""
            <b>{entry['file']['filename']}</b><br>
            Camera: {cam.get('make')} {cam.get('model')}<br>
            Time: {ts.get('datetime_original', 'Unknown')}<br>
            Lat: {gps['latitude']}, Lon: {gps['longitude']}<br>
            <a href="{gps['maps_url']}" target="_blank">Open in Maps</a>
        """
        folium.Marker(
            location=[gps["latitude"], gps["longitude"]],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=entry["file"]["filename"],
            icon=folium.Icon(color="red", icon="camera", prefix="fa"),
        ).add_to(m)

    m.save(output_path)
    return output_path