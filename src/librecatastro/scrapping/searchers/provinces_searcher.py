#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.librecatastro.scrapping.scrapper import Scrapper
from src.librecatastro.scrapping.searcher import Searcher
from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class ProvincesSearcher(Searcher):
    def __init__(self):
        super().__init__()

    @classmethod
    def search_by_provinces(cls, scrapper, prov_list, pictures=False, start_from=''):
        scrapper.process_search_by_provinces(prov_list, pictures, start_from)

    @classmethod
    def list_provinces(cls):
        dotmap = Scrapper.get_provinces()
        provinces = dotmap.consulta_provinciero.provinciero.prov
        for province in provinces:
            logger.debug(province.np)

    @classmethod
    def list_cities(cls, prov_name):
        dotmap = Scrapper.get_cities(prov_name)
        cities = dotmap.consulta_municipiero.municipiero.muni
        for city in cities:
            logger.debug(city.nm)
        return
