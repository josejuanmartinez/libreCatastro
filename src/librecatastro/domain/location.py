#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.utils.cadastro_logger import CadastroLogger

logger = CadastroLogger(__name__).logger


class Location:
    def __init__(self, longitude, latitude):
        self.lon = float(longitude) if longitude is not None else None
        self.lat = float(latitude) if latitude is not None else None

    def to_json(self):
        if self.lon is None and self.lat is None:
            return None
        else:
            return dict(lon=self.lon, lat=self.lat)