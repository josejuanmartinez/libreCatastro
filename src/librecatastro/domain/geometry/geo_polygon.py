import json
from collections import namedtuple

from shapely.geometry import Point, Polygon

from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class GeoPolygon:

    def __init__(self, file):
        self.polygon = None
        try:
            with open(file, "r") as f:
                content = f.read()

                data = json.loads(content, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
                points = data.geo_polygon.location.points
                points_list = []
                for point in points:
                    points_list.append((point.lon, point.lat))
                self.polygon = Polygon(points_list)
        except Exception as e:
            logger.error("{} is not formatted properly. Please take a look at the examples.".format(file))

    def is_point_in_polygon(self, lon, lat):
        p = Point(lon, lat)
        return self.polygon.contains(p)

    def get_bounding_box(self):
        pass
