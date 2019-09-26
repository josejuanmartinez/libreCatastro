#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.utils.cadastro_logger import CadastroLogger

logger = CadastroLogger(__name__).logger


class Location:
    """ Class that stores longitude and latitude of a property (xcen, ycen) by Cadaster
    in a format supported by Kibana (longitude=lon, latitude=lat)"""
    def __init__(self, longitude, latitude):
        self.lon = float(longitude) if longitude is not None else None
        self.lat = float(latitude) if latitude is not None else None

    def to_json(self):
        """ Transforms an object of this class into a json dict """
        if self.lon is None and self.lat is None:
            return None
        else:
            return dict(lon=self.lon, lat=self.lat)