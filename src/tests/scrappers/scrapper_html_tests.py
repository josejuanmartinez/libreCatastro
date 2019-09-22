#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from src.librecatastro.scrapping.parsers.parser_html import ScrapperHTML, ParserHTML


class ScrapperHTMLTests(unittest.TestCase):

    def test_cadaster_full_returns_html(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('0083101WK2008S0001PD')
        self.assertEqual(len(cadaster_list), 1)
        html, picture = cadaster_list[0]
        self.assertIsNotNone(html)
        self.assertIsNone(picture)

    def test_cadaster_full_with_picture_returns_html_and_picture(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('0083101WK2008S0001PD', pictures=True)
        self.assertEqual(len(cadaster_list), 1)
        html, picture = cadaster_list[0]
        self.assertIsNotNone(html)
        self.assertIsNotNone(picture)

    def test_cadaster_half_site_lot_returns_html(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('45134A02500003')
        self.assertEqual(len(cadaster_list), 1)
        html, picture = cadaster_list[0]
        self.assertIsNotNone(html)
        self.assertIsNone(picture)

    def test_cadaster_half_site_lot_returns_html_and_picture(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('45134A02500003', pictures=True)
        self.assertEqual(len(cadaster_list), 1)
        html, picture = cadaster_list[0]
        self.assertIsNotNone(html)
        self.assertIsNotNone(picture)

    def test_cadaster_full_with_constructions_returns_html_and_picture(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('5036901NH2553N0001HB')
        self.assertEqual(len(cadaster_list), 1)
        html, picture = cadaster_list[0]
        self.assertIsNotNone(html)
        self.assertIsNone(picture)

    def test_cadaster_no_cp_returns_html(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('06145A00500028')
        self.assertEqual(len(cadaster_list), 1)
        html, picture = cadaster_list[0]
        self.assertIsNotNone(html)
        self.assertIsNone(picture)

    def test_cadaster_multiparcela_returns_list_of_2(self):
        cadaster_list = ScrapperHTML.scrap_cadaster('22282A00900547')
        self.assertEqual(len(cadaster_list), 2)


if __name__ == '__main__':
    unittest.main()
