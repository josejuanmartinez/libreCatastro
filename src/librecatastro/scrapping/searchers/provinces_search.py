#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dotmap import DotMap

from src.librecatastro.scrapping.scrapper import Scrapper
from src.librecatastro.scrapping.search import Search
from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class ProvincesSearch(Search):
    def __init__(self):
        super().__init__()

    @classmethod
    def scrap_provinces(cls, scrapper, prov_list, pictures=False, start_from=''):
        scrapper.scrap_provinces(prov_list, pictures, start_from)

    @classmethod
    def list_provinces(cls):
        logger.debug(DotMap.pprint(Scrapper.get_provinces()))
        return

    @classmethod
    def list_cities(cls, prov_name):
        logger.debug(DotMap.pprint(Scrapper.get_cities(prov_name)))
        return
