#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from time import sleep

from dotmap import DotMap

from src.librecatastro.domain.cadaster_entry.cadaster_entry_xml import CadasterEntryXML
from src.librecatastro.scrapping.format.scrapper_xml import ScrapperXML
from src.settings import config


class ScrapperXMLTests(unittest.TestCase):
    def test_scrapper_retrieves_dict_provinces(self):
        self.assertEqual(ScrapperXML.get_provinces().consulta_provinciero.control.cuprov, '48')
        sleep(config['sleep_time'])

    def test_scrapper_retrieves_dict_cities(self):
        self.assertEqual(ScrapperXML.get_cities('ALACANT').consulta_municipiero.control.cumun, '141')
        sleep(config['sleep_time'])

    def test_scrapper_retrieves_dict_addresses(self):
        self.assertEqual(ScrapperXML.get_addresses('ALACANT','AGOST').consulta_callejero.control.cuca, '117')
        sleep(config['sleep_time'])

    def test_scrapper_retrieves_dict_addresses_iter(self):
        iterator = ScrapperXML.get_address_iter()
        address = iterator.__next__()
        self.assertEqual(address[1], '15')
        self.assertEqual(address[3], '7')
        sleep(config['sleep_time'])

    def test_scrapper_creates_cadaster_entry(self):
        dotmap_res = ScrapperXML.get_cadaster_entries_by_cadaster('', '', '6375620YH0567S0001GW')
        self.assertNotEqual(dotmap_res, DotMap())
        sleep(config['sleep_time'])

    def test_scrapper_creates_cadaster_entry_and_stores_in_elasticsearch(self):
        entry = ScrapperXML.get_cadaster_entries_by_cadaster('', '', '6375620YH0567S0001GW')
        cadaster_entry = CadasterEntryXML(entry)
        cadaster_entry.to_elasticsearch()
        self.assertIsNotNone(cadaster_entry.from_elasticsearch())
        sleep(config['sleep_time'])

    def test_multiparcela_creates_n_entries_in_elasticsearch(self):
        prov_name = u'A CORUÑA'
        city_name = u'A BAÑA'
        tv = u'LG'
        nv = u'ARZÓN'
        num = 21
        entry = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num)
        counter = 0
        for site in entry.consulta_dnp.lrcdnp.rcdnp:
            cadaster = site.rc.pc1 + \
                       site.rc.pc2 + \
                       site.rc.car + \
                       site.rc.cc1 + \
                       site.rc.cc2
            sub_entry = ScrapperXML.get_cadaster_entries_by_cadaster(prov_name, city_name, cadaster)
            cadaster_entry = CadasterEntryXML(sub_entry)
            cadaster_entry.to_elasticsearch()
            self.assertIsNotNone(cadaster_entry.from_elasticsearch())
            sleep(config['sleep_time'])
            counter += 1
        self.assertEqual(counter, 2)

    def test_no_use_creates_entry_in_elasticsearch(self):
        prov_name = u'A CORUÑA'
        city_name = u'A BAÑA'
        tv = u'LG'
        nv = u'BARCALA'
        num = 5
        entry = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num)
        for site in entry.consulta_dnp.lrcdnp.rcdnp:
            cadaster = site.rc.pc1 + \
                       site.rc.pc2 + \
                       site.rc.car + \
                       site.rc.cc1 + \
                       site.rc.cc2
            sub_entry = ScrapperXML.get_cadaster_entries_by_cadaster(prov_name, city_name, cadaster)
            cadaster_entry = CadasterEntryXML(sub_entry)
            cadaster_entry.to_elasticsearch()
            self.assertIsNotNone(cadaster_entry.from_elasticsearch())
            sleep(config['sleep_time'])

    def test_no_es_pt_pu_creates_entry_in_elasticsearch(self):
        prov_name = u'A CORUÑA'
        city_name = u'A BAÑA'
        tv = u'RU'
        nv = u'CASTELAO'
        num = 1
        entry = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num)
        for site in entry.consulta_dnp.lrcdnp.rcdnp:
            cadaster = site.rc.pc1 + \
                       site.rc.pc2 + \
                       site.rc.car + \
                       site.rc.cc1 + \
                       site.rc.cc2
            sub_entry = ScrapperXML.get_cadaster_entries_by_cadaster(prov_name, city_name, cadaster)
            cadaster_entry = CadasterEntryXML(sub_entry)
            cadaster_entry.to_elasticsearch()
            self.assertIsNotNone(cadaster_entry.from_elasticsearch())
            sleep(config['sleep_time'])

    def test_no_es_pt_pu_creates_entry_in_elasticsearch_2(self):
        # CL BEATAS 4 MADRID ALCALA DE HENARES
        prov_name = u'MADRID'
        city_name = u'ALCALA DE HENARES'
        tv = u'CL'
        nv = u'BEATAS'
        num = 4
        entry = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num)
        for site in entry.consulta_dnp.lrcdnp.rcdnp:
            cadaster = site.rc.pc1 + \
                       site.rc.pc2 + \
                       site.rc.car + \
                       site.rc.cc1 + \
                       site.rc.cc2
            sub_entry = ScrapperXML.get_cadaster_entries_by_cadaster(prov_name, city_name, cadaster)
            cadaster_entry = CadasterEntryXML(sub_entry)
            cadaster_entry.to_elasticsearch()
            self.assertIsNotNone(cadaster_entry.from_elasticsearch())
            sleep(config['sleep_time'])

    def test_multiparcela_coord_creates_n_entries(self):
        lon = -9.2503
        lat = 42.9723
        self.assertEqual(len(ScrapperXML.scrap_coord(lon, lat, True)), 2)

    def test_multiparcela_address_creates_n_entries(self):
        prov_name = u'MADRID'
        city_name = u'AJALVIR'
        tv = u'CL'
        nv = u'CANARIAS'
        num = 7
        cadaster = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, num)
        self.assertEqual(len(ScrapperXML.process_xml_by_address(cadaster, prov_name, city_name, tv, nv, False)), 8)

    def test_multiparcela_address_creates_n_entries_2(self):
        prov_name = u'MADRID'
        city_name = u'AJALVIR'
        tv = u'CL'
        nv = u'CALVARIO'
        num = 38
        cadaster = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, num)
        self.assertEqual(len(ScrapperXML.process_xml_by_address(cadaster, prov_name, city_name, tv, nv, False)), 8)


if __name__ == '__main__':
    unittest.main()
