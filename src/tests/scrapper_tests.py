import unittest

from src.librecatastro.catastro_scrapper import CadastroScrapper
from src.utils.elasticsearch_utils import ElasticSearchUtils


class MyTestCase(unittest.TestCase):

    def test_remove_index_elasticsearch_works(self):
        ElasticSearchUtils.remove_index()
        assert True

    def test_create_index_elasticsearch_works(self):
        ElasticSearchUtils.create_index()
        assert True

    def test_coordinate_creates_cadaster(self):
        cadaster_list = CadastroScrapper.scrap_coord(-3.68, 40.47)
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertEqual(cadaster.cadaster, '2302909VK4820A0001GK')

    def test_coordinate_multiparcela_creates_cadaster_2(self):
        cadaster_list = CadastroScrapper.scrap_coord(-0.33, 39.47)
        self.assertTrue(len(cadaster_list) > 1)

    def test_coordinate_creates_cadaster_and_stores_in_elasticsearch(self):
        cadaster_list = CadastroScrapper.scrap_coord(-3.68, 40.47)
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        cadaster.to_elasticsearch()
        self.assertIsNotNone(cadaster.from_elasticsearch())

    def test_cadaster_site_lot_creates_cadaster_and_sets_site_lot(self):
        cadaster_list = CadastroScrapper.scrap_cadaster('45134A02500003')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertEqual(cadaster.address.site, '25')
        self.assertEqual(cadaster.address.lot, '3')

    def test_cadaster_full_creates_cadaster(self):
        cadaster_list = CadastroScrapper.scrap_cadaster('0083101WK2008S0001PD')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertEqual(cadaster.address.city, 'ALMONACID DEL MARQUESADO')
        self.assertEqual(cadaster.address.province, 'CUENCA')

    def test_cadaster_half_creates_cadaster(self):
        cadaster_list = CadastroScrapper.scrap_cadaster('0183001WK2008S')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertEqual(cadaster.address.city, 'ALMONACID DEL MARQUESADO')
        self.assertEqual(cadaster.address.province, 'CUENCA')

    def test_cadaster_half_creates_cadaster_2(self):
        cadaster_list = CadastroScrapper.scrap_cadaster('21012A03100046')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertEqual(cadaster.address.province, 'HUELVA')

    def test_cadaster_no_cp_creates_cadaster(self):
        cadaster_list = CadastroScrapper.scrap_cadaster('06145A00500028')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertIsNone(cadaster.address.cp)
        self.assertEqual(cadaster.address.province, 'BADAJOZ')

    def test_cadaster_multiparcela_returns_list_of_2(self):
        cadaster_list = CadastroScrapper.scrap_cadaster('22282A00900547')
        self.assertEqual(len(cadaster_list), 2)

    def test_cadaster_is_stored_in_elasticsearch(self):
        cadaster_list = CadastroScrapper.scrap_cadaster('0183001WK2008S')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        cadaster.to_elasticsearch()
        self.assertIsNotNone(cadaster.from_elasticsearch())

    def scrap_random_until_x_times_found(self, times):
        cadaster_list = CadastroScrapper.scrap_results_random_x_times(times)
        self.assertTrue(len(cadaster_list) >= times)
        return cadaster_list

    def test_scrap_random_until_5_found(self):
        self.scrap_random_until_x_times_found(5)

    def test_scrap_random_until_5_is_stored_in_elasticsearch(self):
        cadaster_list = self.scrap_random_until_x_times_found(5)
        for cadaster in cadaster_list:
            cadaster.to_elasticsearch()
            self.assertIsNotNone(cadaster.from_elasticsearch())

    def test_scrap_random_until_1_is_stored_in_elasticsearch(self):
        cadaster_list = self.scrap_random_until_x_times_found(1)
        for cadaster in cadaster_list:
            cadaster.to_elasticsearch()
            self.assertIsNotNone(cadaster.from_elasticsearch())

    """def test_create_ontology_with_one_scrap_result(self):
        ontology_converter = OntologyConverter()
        results = list()
        results.append(CadastroScrapper.scrap_coord(-3.68, 40.47))
        print(ontology_converter.cadastro_dict_to_ontology(results))
    """


if __name__ == '__main__':
    unittest.main()
