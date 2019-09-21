#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class Parser:
    """Generic Parser class"""

    def __init__(self):
        pass

    ''' Processing signatures'''
    @classmethod
    def process_search_by_coordinates(cls, x, y, pictures=False):
        pass

    @classmethod
    def process_search_by_provinces(cls, prov_list, pictures=False):
        pass