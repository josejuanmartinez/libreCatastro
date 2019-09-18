import os

root_path = os.path.dirname(os.path.abspath(__file__))

config = {
    "separator": "####",
    "elasticsearch-index": "cadaster",
    "error_log_file": os.path.join(root_path, 'logs', 'log'),
    "tracking_log_file": os.path.join(root_path, 'logs', 'track'),
    "scale": 1000000,
    "coordinates_path": os.path.join(root_path, 'coordinates'),
    "not_available_via_XML": "(Not available via XML)",
    "sleep_time": 5,
    "sleep_dos_time": 300
}
