#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

from src.librecatastro.scrapping.format.scrapper_html import ScrapperHTML
from src.librecatastro.scrapping.format.scrapper_xml import ScrapperXML
from src.librecatastro.scrapping.searchers.coordinates_search import CoordinatesSearch
from src.librecatastro.scrapping.searchers.provinces_search import ProvincesSearch
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

    scrapper = ScrapperHTML if args.html else ScrapperXML

    filenames = args.filenames
    pictures = args.pictures
    provinces = args.provinces
    startcity = args.startcity

    if args.listprovinces:
        ProvincesSearch.list_provinces()
        exit(0)

    if len(args.listcities) == 1:
        ProvincesSearch.list_cities(args.listcities[0])
        exit(0)

    if args.coords:
        CoordinatesSearch.scrap_coordinates(scrapper, filenames, pictures)
    else:
        ProvincesSearch.scrap_provinces(scrapper, provinces, pictures, startcity)
