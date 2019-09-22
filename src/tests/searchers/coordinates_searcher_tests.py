import os
import unittest

from src.librecatastro.domain.geometry.geo_polygon import GeoPolygon
from src.librecatastro.scrapping.parsers.parser_html import ParserHTML
from src.librecatastro.scrapping.searchers.coordinates_searcher import CoordinatesSearcher
from src.settings import config


class CoordinatesSearcherTests(unittest.TestCase):

    def search_random_until_x_times_found_by_html(self, times):
        polygon = GeoPolygon(os.path.join(config['coordinates_path'], 'spain_polygon.json'))
        coord = polygon.get_bounding_box()
        cadaster_list = CoordinatesSearcher.search_by_coordinates_random_max_n_matches(times, int(coord[0] * config['scale']), int(coord[2] * config['scale']), int(coord[1] * config['scale']), int(coord[3] * config['scale']), ParserHTML)
        self.assertTrue(len(cadaster_list) >= times)
        return cadaster_list

    def test_search_random_until_5_found(self):
        self.search_random_until_x_times_found_by_html(5)

    def test_search_random_until_5_is_stored_in_elasticsearch(self):
        cadaster_list = self.search_random_until_x_times_found_by_html(5)
        for cadaster in cadaster_list:
            cadaster.to_elasticsearch()
            self.assertIsNotNone(cadaster.from_elasticsearch())

    def test_search_random_until_1_is_stored_in_elasticsearch(self):
        cadaster_list = self.search_random_until_x_times_found_by_html(1)
        for cadaster in cadaster_list:
            cadaster.to_elasticsearch()
            self.assertIsNotNone(cadaster.from_elasticsearch())

    def test_loading_point_is_in_polygon_returns_true(self):
        polygon = GeoPolygon(os.path.join(config['coordinates_path'], 'spain_polygon.json'))
        self.assertTrue(polygon.is_point_in_polygon(lon=-5.295410156250001, lat=40.069664523297774))

    def test_loading_point_is_not_in_polygon_returns_false(self):
        polygon = GeoPolygon(os.path.join(config['coordinates_path'], 'spain_polygon.json'))
        self.assertFalse(polygon.is_point_in_polygon(lon=-1.9335937500000002, lat=48.31242790407178))

    def test_polygon_has_correct_bounding_box(self):
        polygon = GeoPolygon(os.path.join(config['coordinates_path'], 'spain_polygon.json'))
        self.assertIsNotNone(polygon.get_bounding_box())


if __name__ == '__main__':
    unittest.main()
