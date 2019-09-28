#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.librecatastro.scrapping.scrapper import Scrapper
from src.librecatastro.scrapping.searcher import Searcher
from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class ProvincesSearcher(Searcher):
    """
    Class that allows searching Cadastro by provinces, cities, addresses
    """
    def __init__(self):
        super().__init__()

    @classmethod
    def search_by_provinces(cls, scrapper, prov_list, pictures=False, start_from=''):
        """
        Searchs Cadastro by a list of provinces. We can optionally set if we want
        pictures to be scrapped as well (of the house plan) or if we want to start from
        a specific city. Example: I want to scrap Madrid province starting alphabetically
        from 'Fuenlabrada'
        :param scrapper: XML or HTML Scrapper
        :param prov_list: List of province names
        :param pictures: True if we want house plan pictures to be scrapped. False otherwise.
        :param start_from: Name of the city we want to start from (from the first province)
        """
        scrapper.process_search_by_provinces(prov_list, pictures, start_from)

    @classmethod
    def list_provinces(cls):
        """
        Lists province names from Cadastro
        """
        dotmap = Scrapper.get_provinces()
        provinces = dotmap.consulta_provinciero.provinciero.prov
        for province in provinces:
            logger.debug(province.np)

    @classmethod
    def list_cities(cls, prov_name):
        """
        Lists city names from Cadastro
        """
        dotmap = Scrapper.get_cities(prov_name)
        cities = dotmap.consulta_municipiero.municipiero.muni
        for city in cities:
            logger.debug(city.nm)
        return
