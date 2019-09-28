#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod

from src.utils.catastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class Parser:
    """ Parser signature class that defines common interfaces for HTMLParser and XMLParser
    classes """

    def __init__(self):
        pass

    ''' Signatures'''
    @classmethod
    @abstractmethod
    def process_search_by_coordinates(cls, x, y, pictures=False):
        pass

    @classmethod
    @abstractmethod
    def process_search_by_provinces(cls, prov_list, pictures=False):
        pass
