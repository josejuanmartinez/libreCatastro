#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest

from src.librecatastro.domain.geometry.geo_polygon import GeoPolygon
from src.librecatastro.scrapping.parsers.parser_html import ScrapperHTML
from src.librecatastro.scrapping.searchers.coordinates_searcher import CoordinatesSearcher
from src.settings import config
from src.utils.elasticsearch_utils import ElasticSearchUtils


class ScrapperHTMLTests(unittest.TestCase):

    def test_remove_index_elasticsearch_works(self):
        ElasticSearchUtils.remove_index()
        assert True

    def test_create_index_elasticsearch_works(self):
        ElasticSearchUtils.create_index()
        assert True

    def test_coordinate_creates_cadaster(self):
        cadaster_list = ScrapperHTML.parse_coord(-3.68, 40.47)
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertEqual(cadaster.cadaster, '2302909VK4820A0001GK')

    def test_coordinate_multiparcela_creates_cadaster(self):
        cadaster_list = ScrapperHTML.parse_coord(-0.33, 39.47)
        self.assertTrue(len(cadaster_list) > 1)

    def test_coordinate_creates_cadaster_and_stores_in_elasticsearch(self):
        cadaster_list = ScrapperHTML.parse_coord(-3.68, 40.47)
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        cadaster.to_elasticsearch()
        self.assertIsNotNone(cadaster.from_elasticsearch())

    def test_cadaster_site_lot_creates_cadaster_and_sets_site_lot(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('45134A02500003')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertEqual(cadaster.address.site, '25')
        self.assertEqual(cadaster.address.lot, '3')

    def test_cadaster_full_creates_cadaster(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('0083101WK2008S0001PD')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertEqual(cadaster.address.city, 'ALMONACID DEL MARQUESADO')
        self.assertEqual(cadaster.address.province, 'CUENCA')

    def test_cadaster_full_creates_cadaster_with_constructions(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('5036901NH2553N0001HB')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertTrue(len(cadaster.constructions) > 0)

    def test_cadaster_half_creates_cadaster(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('0183001WK2008S')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertEqual(cadaster.address.city, 'ALMONACID DEL MARQUESADO')
        self.assertEqual(cadaster.address.province, 'CUENCA')

    def test_cadaster_half_creates_cadaster_2(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('21012A03100046')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertEqual(cadaster.address.province, 'HUELVA')

    def test_cadaster_no_cp_creates_cadaster(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('06145A00500028')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        self.assertIsNone(cadaster.address.cp)
        self.assertEqual(cadaster.address.province, 'BADAJOZ')

    def test_cadaster_multiparcela_returns_list_of_2(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('22282A00900547')
        self.assertEqual(len(cadaster_list), 2)

    def test_cadaster_is_stored_in_elasticsearch(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('0183001WK2008S')
        self.assertEqual(len(cadaster_list), 1)
        cadaster = cadaster_list[0]
        cadaster.to_elasticsearch()
        self.assertIsNotNone(cadaster.from_elasticsearch())

    def scrap_random_until_x_times_found(self, times):
        polygon = GeoPolygon(os.path.join(config['coordinates_path'], 'spain_polygon.json'))
        coord = polygon.get_bounding_box()
        cadaster_list = CoordinatesSearcher.search_by_coordinates_random_max_n_matches(times, int(coord[0] * config['scale']), int(coord[2] * config['scale']), int(coord[1] * config['scale']), int(coord[3] * config['scale']), ScrapperHTML)
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

    def test_loading_point_is_in_polygon_returns_true(self):
        polygon = GeoPolygon(os.path.join(config['coordinates_path'], 'spain_polygon.json'))
        self.assertTrue(polygon.is_point_in_polygon(lon=-5.295410156250001, lat=40.069664523297774))

    def test_loading_point_is_not_in_polygon_returns_false(self):
        polygon = GeoPolygon(os.path.join(config['coordinates_path'], 'spain_polygon.json'))
        self.assertFalse(polygon.is_point_in_polygon(lon=-1.9335937500000002, lat=48.31242790407178))

    def test_polygon_has_correct_bounding_box(self):
        polygon = GeoPolygon(os.path.join(config['coordinates_path'], 'spain_polygon.json'))
        self.assertIsNotNone(polygon.get_bounding_box())

    def test_if_pictures_enabled_picture_is_set(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('06145A00500028', pictures=True)
        self.assertIsNotNone(cadaster_list[0].picture)


if __name__ == '__main__':
    unittest.main()
