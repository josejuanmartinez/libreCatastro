#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from collections import namedtuple

from shapely.geometry import Point, Polygon

from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class GeoPolygon:
    """
    A GeoPolygon is a series of lon,lat points in a json. This class uses shapely.geometry
    to convert points into Point objects and these into a Polygon class.
    """

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
        """
        Check if a point (lot, lat) is inside this Polygon
        :param lon: longitude
        :param lat: latitude
        :return: True if point is inside polygon. False otherwise
        """
        p = Point(lon, lat)
        return self.polygon.contains(p)

    def get_bounding_box(self):
        """
        Gets the bounding box of a polygon
        :return: A Box object from shapely.geometry containing inside the Polygon
        """
        if self.polygon is not None:
            return self.polygon.bounds
        else:
            return None
