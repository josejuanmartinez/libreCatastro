#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from time import sleep

from src.librecatastro.domain.cadaster_entry.cadaster_entry_xml import CadasterEntryXML
from src.librecatastro.scrapping.parsers.parser_xml import ParserXML
from src.librecatastro.scrapping.scrappers.scrapper_xml import ScrapperXML
from src.settings import config


class ScrapperXMLTests(unittest.TestCase):

    def test_scrapper_retrieves_dict_addresses_iter(self):
        iterator = ScrapperXML.get_address_iter()
        address = iterator.__next__()
        self.assertEqual(address[1], '15')
        self.assertEqual(address[3], '7')

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
            self.assertTrue(cadaster_entry.from_elasticsearch())
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
            self.assertTrue(cadaster_entry.from_elasticsearch())
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
            self.assertTrue(cadaster_entry.from_elasticsearch())
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
            self.assertTrue(cadaster_entry.from_elasticsearch())
            sleep(config['sleep_time'])

    def test_multiparcela_coord_creates_n_entries(self):
        lon = -9.2503
        lat = 42.9723
        self.assertEqual(len(ParserXML.process_search_by_coordinates(lon, lat, True)), 2)

    def test_multiparcela_address_creates_n_entries(self):
        prov_name = u'MADRID'
        city_name = u'AJALVIR'
        tv = u'CL'
        nv = u'CANARIAS'
        num = 7
        cadaster = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, num)
        self.assertEqual(len(ParserXML.process_xml_by_address(cadaster, prov_name, city_name, tv, nv, False)), 8)

    def test_multiparcela_address_creates_n_entries_2(self):
        prov_name = u'MADRID'
        city_name = u'AJALVIR'
        tv = u'CL'
        nv = u'CALVARIO'
        num = 38
        cadaster = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, num)
        self.assertEqual(len(ParserXML.process_xml_by_address(cadaster, prov_name, city_name, tv, nv, False)), 8)

    def test_poligono_or_rural_creates_entry(self):
        tv = 'CL'
        nv = 'TORREJON'
        num = 30
        prov_name = 'MADRID'
        city_name = 'AJALVIR'
        cadaster = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, num)
        self.assertEqual(len(ParserXML.process_xml_by_address(cadaster, prov_name, city_name, tv, nv, False)), 16)

    def test_coordinates_are_in_good_format(self):
        tv = 'CL'
        nv = 'DE BENICARLO'
        num = 1
        prov_name = 'MADRID'
        city_name = 'GALAPAGAR'
        xml = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, num)
        cadaster_entry = ParserXML.process_xml_by_address(xml, prov_name, city_name, tv, nv, False)
        self.assertEqual(cadaster_entry[0].location.lat, 40.6249762551374)
        self.assertEqual(cadaster_entry[0].location.lon, -4.02755522611211)

    def test_multiparcela_coordinates_are_in_good_format(self):
        tv = 'CL'
        nv = 'SAN VICENTE'
        num = 26
        prov_name = 'ALACANT'
        city_name = 'ALICANTE/ALACANT'
        xml = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, num)
        cadaster_entries = ParserXML.process_xml_by_address(xml, prov_name, city_name, tv, nv, False)
        for cadaster_entry in cadaster_entries:
            self.assertEqual(cadaster_entry.location.lat, 38.3495195831056)
            self.assertEqual(cadaster_entry.location.lon, -0.484612452235845)


if __name__ == '__main__':
    unittest.main()
