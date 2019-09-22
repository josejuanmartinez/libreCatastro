import unittest

from src.librecatastro.scrapping.parsers.parser_html import ParserHTML
from src.librecatastro.scrapping.scrappers.scrapper_html import ScrapperHTML


class ParserHTMLTests(unittest.TestCase):

    def test_search_by_coordinates_creates_and_stores_in_elasticsearch(self):
        cadaster_list = ParserHTML.process_search_by_coordinates(-3.47600944027389, 40.5370635727521)
        self.assertEqual(len(cadaster_list), 14)
        for cadaster in cadaster_list:
            self.assertIsNotNone(cadaster.from_elasticsearch())

    def test_search_by_provinces_creates_and_stores_in_elasticsearch(self):
        cadaster_list = ParserHTML.process_search_by_provinces(['MADRID'], max_times=1)
        self.assertEqual(len(cadaster_list), 14)
        for cadaster in cadaster_list:
            self.assertIsNotNone(cadaster.from_elasticsearch())

    def test_search_site_lot_is_set(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('45134A02500003')
        html, picture = cadaster_list[0]
        cadaster = ParserHTML.parse_html_parcela(html)
        self.assertIsNotNone(cadaster.address.site)
        self.assertIsNotNone(cadaster.address.lot)

    def test_search_constructions_are_set(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('5036901NH2553N0001HB')
        html, picture = cadaster_list[0]
        cadaster = ParserHTML.parse_html_parcela(html)
        self.assertTrue(len(cadaster.constructions)>0)

    def test_seach_no_cp_is_correctly_set(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('06145A00500028')
        html, picture = cadaster_list[0]
        cadaster = ParserHTML.parse_html_parcela(html)
        self.assertIsNone(cadaster.address.cp)

    def test_search_multiparcela_2_cadasters_are_set(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('22282A00900547')
        for cadaster in cadaster_list:
            html, picture = cadaster
            cadaster = ParserHTML.parse_html_parcela(html)
            self.assertIsNotNone(cadaster.cadaster)


if __name__ == '__main__':
    unittest.main()
