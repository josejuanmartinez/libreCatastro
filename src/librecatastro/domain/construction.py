#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.librecatastro.domain.reform import Reform


class Construction:
    """ Class that stores constructions / reforms of a property"""
    def __init__(self, construction):
        self.use = construction[u'uso']
        self.doorway = construction[u'escalera']
        self.floor = construction[u'planta']
        self.door = construction[u'puerta']
        self.surface = construction[u'superficie']
        self.reform = Reform(dict(tipo=construction[u'tipo'], fecha=construction[u'fecha']))

    def to_json(self):
        """ Transforms an object of this class into a json dict """
        return dict(use=self.use, doorway=self.doorway, floor=self.floor, door=self.door, surface=self.surface, reform=self.reform)
