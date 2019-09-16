import os

root_path = os.path.dirname(os.path.abspath(__file__))

config = {
    "separator": "####",
    "elasticsearch-index": "cadaster",
    "log_config": os.path.join(root_path, 'logger.cfg'),
    "log": os.path.join(root_path, 'logs', 'log')
}