import os

root_path = os.path.dirname(os.path.abspath(__file__))

config = {
    "separator": "####",
    "elasticsearch-index": "cadaster",
    "error_log_file": os.path.join(root_path, 'logs', 'log'),
    "tracking_log_file": os.path.join(root_path, 'logs', 'track')
}
