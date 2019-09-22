#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from src.librecatastro.scrapping.scrapper import Scrapper
from src.librecatastro.scrapping.scrappers.scrapper_xml import ScrapperXML
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class ServerHealthTests(unittest.TestCase):
    def test_scrapper_retrieves_dict_provinces(self):
        try:
            self.assertEqual(Scrapper.get_provinces().consulta_provinciero.control.cuprov, '48')
        except:
            logger.debug(config['servers_down_message_001'])

    def test_scrapper_retrieves_dict_cities(self):
        try:
            self.assertEqual(Scrapper.get_cities('ALACANT').consulta_municipiero.control.cumun, '141')
        except:
            logger.debug(config['servers_down_message_001'])

    def test_scrapper_retrieves_dict_addresses(self):
        try:
            self.assertEqual(Scrapper.get_addresses('ALACANT', 'AGOST').consulta_callejero.control.cuca, '117')
        except:
            logger.debug(config['servers_down_message_001'])

    def test_get_cadaster_entries_by_cadaster_is_up(self):
        cadasters = ['2503906VK4820D0001MX']
        try:
            for cadaster in cadasters:
                ScrapperXML.get_cadaster_entries_by_cadaster('', '', cadaster)
        except:
            logger.debug(config['servers_down_message_002'])

    @staticmethod
    def healthcheck():
        suite = unittest.TestLoader().loadTestsFromTestCase(ServerHealthTests)
        unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    unittest.main()
