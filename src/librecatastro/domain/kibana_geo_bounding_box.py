import json
from collections import namedtuple

from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class KibanaGeoBoundingBox:
    def __init__(self, data):
        self.data = json.loads(data, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

    def get_coordinates_tuple(self):
        return KibanaGeoBoundingBox.get_coordinates_tuple_static(self.data)

    @staticmethod
    def get_coordinates_tuple_static(data):
        location = data.geo_bounding_box.location
        return int(location.top_left.lon * config['scale']), int(location.bottom_right.lon * config['scale']), int(location.bottom_right.lat * config['scale']), int(location.top_left.lat * config['scale'])

    @staticmethod
    def get_coordinate_tuple_from_file(file):
        f = open(file, "r")
        content = f.read()
        try:
            data = json.loads(content, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            return KibanaGeoBoundingBox.get_coordinates_tuple_static(data)
        except:
            logger.error("{} is not formatted properly. Please take a look at the examples.".format(file))
            return None
