import unittest
from time import sleep

from src.librecatastro.domain.cadaster_entry.cadaster_entry_xml import CadasterEntryXML
from src.librecatastro.scrapping.format.scrapper_xml import ScrapperXML
from src.settings import config


class ScrapperXMLTests(unittest.TestCase):
    def test_scrapper_retrieves_dict_provinces(self):
        self.assertEqual(ScrapperXML.get_provinces()['consulta_provinciero']['control']['cuprov'], '48')

    def test_scrapper_retrieves_dict_cities(self):
        self.assertEqual(ScrapperXML.get_cities('ALACANT')['consulta_municipiero']['control']['cumun'],'141')
        sleep(config['sleep_time'])

    def test_scrapper_retrieves_dict_addresses(self):
        self.assertEqual(ScrapperXML.get_addresses('ALACANT','AGOST')['consulta_callejero']['control']['cuca'], '117')
        sleep(config['sleep_time'])

    def test_scrapper_creates_cadaster_entry(self):
        print(ScrapperXML.get_cadaster_entries_by_cadaster('','', '6375620YH0567S0001GW'))
        sleep(config['sleep_time'])

    def test_scrapper_creates_cadaster_entry_and_stores_in_elasticsearch(self):
        entry = ScrapperXML.get_cadaster_entries_by_cadaster('', '', '6375620YH0567S0001GW')
        cadaster_entry = CadasterEntryXML(entry, None, None)
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
        for site in entry['consulta_dnp']['lrcdnp']['rcdnp']:
            cadaster = site['rc']['pc1'] + \
                       site['rc']['pc2'] + \
                       site['rc']['car'] + \
                       site['rc']['cc1'] + \
                       site['rc']['cc2']
            sub_entry = ScrapperXML.get_cadaster_entries_by_cadaster(prov_name, city_name, cadaster)
            cadaster_entry = CadasterEntryXML(sub_entry, None, None)
            cadaster_entry.to_elasticsearch()
            self.assertIsNotNone(cadaster_entry.from_elasticsearch())
            sleep(config['sleep_time'])

    def test_no_use_creates_entry_in_elasticsearch(self):
        prov_name = u'A CORUÑA'
        city_name = u'A BAÑA'
        tv = u'LG'
        nv = u'BARCALA'
        num = 5
        entry = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num)
        for site in entry['consulta_dnp']['lrcdnp']['rcdnp']:
            cadaster = site['rc']['pc1'] + \
                       site['rc']['pc2'] + \
                       site['rc']['car'] + \
                       site['rc']['cc1'] + \
                       site['rc']['cc2']
            sub_entry = ScrapperXML.get_cadaster_entries_by_cadaster(prov_name, city_name, cadaster)
            cadaster_entry = CadasterEntryXML(sub_entry, None, None)
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
        for site in entry['consulta_dnp']['lrcdnp']['rcdnp']:
            cadaster = site['rc']['pc1'] + \
                       site['rc']['pc2'] + \
                       site['rc']['car'] + \
                       site['rc']['cc1'] + \
                       site['rc']['cc2']
            sub_entry = ScrapperXML.get_cadaster_entries_by_cadaster(prov_name, city_name, cadaster)
            cadaster_entry = CadasterEntryXML(sub_entry, None, None)
            cadaster_entry.to_elasticsearch()
            self.assertIsNotNone(cadaster_entry.from_elasticsearch())
            sleep(config['sleep_time'])


if __name__ == '__main__':
    unittest.main()
