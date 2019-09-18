import unittest
from time import sleep

from src.librecatastro.domain.cadaster_entry.cadaster_entry_xml import CadasterEntryXML
from src.librecatastro.scrapping.format.scrapper_xml import ScrapperXML
from src.settings import config


class ScrapperXMLTests(unittest.TestCase):
    def test_scrapper_retrieves_dict_provinces(self):
        provinces = ScrapperXML.get_provinces()['consulta_provinciero']['provinciero']['prov']
        self.assertTrue(len(provinces) == 48)

    def test_scrapper_retrieves_dict_cities(self):
        provinces = ScrapperXML.get_provinces()['consulta_provinciero']['provinciero']['prov']
        for province in provinces:
            prov_name = province['np']
            cities = ScrapperXML.get_cities(prov_name)
            self.assertTrue(len(cities['consulta_municipiero']['municipiero']['muni']) > 0)

    def test_scrapper_retrieves_dict_addresses(self):
        provinces = ScrapperXML.get_provinces()['consulta_provinciero']['provinciero']['prov']
        for province in provinces:
            prov_name = province['np']
            cities = ScrapperXML.get_cities(prov_name)['consulta_municipiero']['municipiero']['muni']
            for city in cities:
                city_name = city['nm']
                addresses = ScrapperXML.get_addresses(prov_name, city_name)
                self.assertTrue(len(addresses['consulta_callejero']['callejero']['calle']) > 0)
                return

    def test_scrapper_retrieves_dict_properties(self):
        provinces = ScrapperXML.get_provinces()['consulta_provinciero']['provinciero']['prov']
        for province in provinces:
            prov_name = province['np']
            cities = ScrapperXML.get_cities(prov_name)['consulta_municipiero']['municipiero']['muni']
            for city in cities:
                city_name = city['nm']
                addresses = ScrapperXML.get_addresses(prov_name, city_name)['consulta_callejero']['callejero']['calle']
                for address in addresses:
                    address_dir = address['dir']
                    tv = address_dir['tv']
                    nv = address_dir['nv']

                    num_scrapping_fails = 10
                    counter = 1
                    matches = 0
                    while num_scrapping_fails > 0:
                        cadaster = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, counter)
                        if 'lerr' in cadaster['consulta_numerero'] and \
                                'err' in cadaster['consulta_numerero']['lerr'] and \
                                'cod' in cadaster['consulta_numerero']['lerr']['err'] and\
                                cadaster['consulta_numerero']['lerr']['err']['cod'] == '43':
                            num_scrapping_fails -= 1
                        else:
                            num_scrapping_fails = 10
                            matches += 1

                        counter += 1
                        sleep(5)

                    self.assertTrue(matches > 0)
                    return

    def test_scrapper_creates_cadaster_entry(self):
        results = []
        provinces = ScrapperXML.get_provinces()['consulta_provinciero']['provinciero']['prov']
        for province in provinces:
            prov_name = province['np']
            cities = ScrapperXML.get_cities(prov_name)['consulta_municipiero']['municipiero']['muni']
            for city in cities:
                city_name = city['nm']
                addresses = ScrapperXML.get_addresses(prov_name, city_name)['consulta_callejero']['callejero'][
                    'calle']
                for address in addresses:
                    address_dir = address['dir']
                    tv = address_dir['tv']
                    nv = address_dir['nv']

                    num_scrapping_fails = 10
                    counter = 1
                    while num_scrapping_fails > 0:
                        cadaster = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, counter)
                        if 'lerr' in cadaster['consulta_numerero'] and \
                                'err' in cadaster['consulta_numerero']['lerr'] and \
                                'cod' in cadaster['consulta_numerero']['lerr']['err'] and \
                                cadaster['consulta_numerero']['lerr']['err']['cod'] == '43':
                            num_scrapping_fails -= 1
                        else:
                            num = cadaster['consulta_numerero']['numerero']['nump']['num']['pnp']
                            cadaster_num = cadaster['consulta_numerero']['numerero']['nump']['pc']['pc1'] + \
                                           cadaster['consulta_numerero']['numerero']['nump']['pc']['pc2']

                            coords = ScrapperXML.get_coords_from_cadaster(prov_name, city_name, cadaster_num)
                            lon = coords['consulta_coordenadas']['coordenadas']['coord']['geo']['xcen']
                            lat = coords['consulta_coordenadas']['coordenadas']['coord']['geo']['ycen']
                            num_scrapping_fails = 10

                            entry = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num)
                            cadaster_entry = CadasterEntryXML(entry, lon, lat)
                            results.append(cadaster_entry)

                        counter += 1
                        sleep(5)

                    self.assertTrue(len(results) > 1)
                    return

    def test_scrapper_creates_cadaster_entry_and_stores_in_elasticsearch(self):
        provinces = ScrapperXML.get_provinces()['consulta_provinciero']['provinciero']['prov']
        for province in provinces:
            prov_name = province['np']
            cities = ScrapperXML.get_cities(prov_name)['consulta_municipiero']['municipiero']['muni']
            for city in cities:
                city_name = city['nm']
                addresses = ScrapperXML.get_addresses(prov_name, city_name)['consulta_callejero']['callejero'][
                    'calle']
                for address in addresses:
                    address_dir = address['dir']
                    tv = address_dir['tv']
                    nv = address_dir['nv']

                    num_scrapping_fails = 10
                    counter = 1
                    while num_scrapping_fails > 0:
                        cadaster = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, counter)
                        if 'lerr' in cadaster['consulta_numerero'] and \
                                'err' in cadaster['consulta_numerero']['lerr'] and \
                                'cod' in cadaster['consulta_numerero']['lerr']['err'] and \
                                cadaster['consulta_numerero']['lerr']['err']['cod'] == '43':
                            num_scrapping_fails -= 1
                        else:
                            num = cadaster['consulta_numerero']['numerero']['nump']['num']['pnp']
                            cadaster_num = cadaster['consulta_numerero']['numerero']['nump']['pc']['pc1'] + \
                                           cadaster['consulta_numerero']['numerero']['nump']['pc']['pc2']

                            coords = ScrapperXML.get_coords_from_cadaster(prov_name, city_name, cadaster_num)
                            lon = coords['consulta_coordenadas']['coordenadas']['coord']['geo']['xcen']
                            lat = coords['consulta_coordenadas']['coordenadas']['coord']['geo']['ycen']

                            entry = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num)
                            cadaster_entry = CadasterEntryXML(entry, lon, lat)
                            cadaster_entry.to_elasticsearch()

                            self.assertIsNotNone(cadaster_entry.from_elasticsearch())
                            return

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
