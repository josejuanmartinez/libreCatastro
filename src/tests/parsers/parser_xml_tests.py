import unittest

from src.librecatastro.scrapping.parsers.parser_xml import ParserXML


class ParserXMLTests(unittest.TestCase):

    def test_search_by_coordinates_creates_and_stores_in_elasticsearch(self):
        cadaster_list = ParserXML.process_search_by_coordinates(-3.47600944027389, 40.5370635727521)
        self.assertEqual(len(cadaster_list), 14)
        for cadaster in cadaster_list:
            self.assertTrue(cadaster.from_elasticsearch())

    def test_search_by_provinces_creates_and_stores_in_elasticsearch(self):
        cadaster_list = ParserXML.process_search_by_provinces(['MADRID'], max_times=1)
        self.assertEqual(len(cadaster_list), 1)
        for cadaster in cadaster_list:
            self.assertTrue(cadaster.from_elasticsearch())


if __name__ == '__main__':
    unittest.main()
