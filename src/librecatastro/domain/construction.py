#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.librecatastro.domain.reform import Reform


class Construction:
    def __init__(self, construction):
        self.use = construction[u'uso']
        self.doorway = construction[u'escalera']
        self.floor = construction[u'planta']
        self.door = construction[u'puerta']
        self.surface = construction[u'superficie']
        self.reform = Reform(dict(tipo=construction[u'tipo'], fecha=construction[u'fecha']))

    def to_json(self):
        return dict(use=self.use, doorway=self.doorway, floor=self.floor, door=self.door, surface=self.surface, reform=self.reform)
