#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Reform:
    """ Class that stores type of reform(reforma) and year """
    def __init__(self, reform_data):
        self.type = reform_data['tipo'].strip()
        self.year = reform_data['fecha'].strip()

    def to_json(self):
        """ Transforms an object of this class into a json dict """
        return dict(type=self.type, year=self.year)