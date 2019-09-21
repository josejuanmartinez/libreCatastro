#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

from src.librecatastro.scrapping.parsers.parser_html import ScrapperHTML
from src.librecatastro.scrapping.parsers.parser_xml import ParserXML
from src.librecatastro.scrapping.searchers.coordinates_searcher import CoordinatesSearcher
from src.librecatastro.scrapping.searchers.provinces_searcher import ProvincesSearcher
from src.settings import config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs the Cadastro Parser')
    parser.add_argument('--coords', action='store_true', dest='coords', default=False)
    parser.add_argument('--filenames', action='store', nargs='+', dest='filenames', default=[])
    parser.add_argument('--provinces', action='store', nargs='+', dest='provinces', default=[])
    parser.add_argument('--sleep', action='store', dest='sleep', type=int, default=5)
    parser.add_argument('--html', dest='html', default=False, action='store_true')
    parser.add_argument('--scale', action='store', dest='scale', type=int, default=10000)
    parser.add_argument('--pictures', action='store_true', dest='pictures', default=False)
    parser.add_argument('--startcity', action='store', dest='startcity', default='')
    parser.add_argument('--listprovinces', action='store_true', dest='listprovinces', default=False)
    parser.add_argument('--listcities', action='store', nargs=1, dest='listcities', default=[])

    args = parser.parse_args(sys.argv[1:])

    if args.sleep:
        config['sleep_time'] = args.sleep

    if args.scale:
        config['scale'] = args.scale

    scrapper = ScrapperHTML if args.html else ParserXML

    filenames = args.filenames
    pictures = args.pictures
    provinces = args.provinces
    startcity = args.startcity

    if args.listprovinces:
        ProvincesSearcher.list_provinces()
        exit(0)

    if len(args.listcities) == 1:
        ProvincesSearcher.list_cities(args.listcities[0])
        exit(0)

    if args.coords:
        CoordinatesSearcher.search_by_coordinates(scrapper, filenames, pictures)
    else:
        ProvincesSearcher.search_by_provinces(scrapper, provinces, pictures, startcity)
