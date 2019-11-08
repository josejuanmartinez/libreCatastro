#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import pprint

from src.librecatastro.scrapping.parsers.parser_html import ParserHTML
from src.librecatastro.scrapping.parsers.parser_xml import ParserXML
from src.librecatastro.scrapping.searchers.coordinates_searcher import CoordinatesSearcher
from src.librecatastro.scrapping.searchers.provinces_searcher import ProvincesSearcher
from src.settings import config
from src.tests.servers_health.server_health_tests import ServerHealthTests

""" Main executable file, that processes all the arguments with ArguentParser
and do different functionalities, like listing provinces, cities, scrapping from HTML,
from XML, based on coordinates files or a list of provinces, etc """

if __name__ == "__main__":
    ''' Definition of command line arguments for ArgumentParser '''
    parser = argparse.ArgumentParser(description='Runs libreCatastro')
    parser.add_argument('--coords', action='store_true', dest='coords', default=False)
    parser.add_argument('--coords-filenames', action='store', nargs='+', dest='filenames', default=[])
    parser.add_argument('--provinces', action='store', nargs='+', dest='provinces', default=[])
    parser.add_argument('--sleep', action='store', dest='sleep', type=int, default=5)
    parser.add_argument('--html', dest='html', default=False, action='store_true')
    parser.add_argument('--scale', action='store', dest='scale', type=int, default=10000)
    parser.add_argument('--pictures', action='store_true', dest='pictures', default=False)
    parser.add_argument('--startcity', action='store', dest='startcity', default='')
    parser.add_argument('--listprovinces', action='store_true', dest='listprovinces', default=False)
    parser.add_argument('--listcities', action='store', nargs=1, dest='listcities', default=[])
    parser.add_argument('--health', action='store_true', dest='health', default=False)

    ''' Parsing of arguments from command line'''
    args = parser.parse_args(sys.argv[1:])

    ''' Configuration of parameters to be overwriten '''
    if args.sleep:
        config['sleep_time'] = args.sleep

    if args.scale:
        config['scale'] = args.scale

    ''' Listing functionality '''
    if args.listprovinces:
        ProvincesSearcher.list_provinces()
        exit(0)

    if len(args.listcities) == 1:
        ProvincesSearcher.list_cities(args.listcities[0])
        exit(0)

    ''' Cadaster server checking '''
    if args.health:
        ServerHealthTests.healthcheck()
        exit(0)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(config)

    ''' Scrapping / Parsing core functionality'''
    parser = ParserHTML if args.html else ParserXML

    filenames = args.filenames
    pictures = args.pictures
    provinces = args.provinces
    startcity = args.startcity

    if args.coords:
        CoordinatesSearcher.search_by_coordinates(parser, filenames, pictures)
    else:
        ProvincesSearcher.search_by_provinces(parser, provinces, pictures, startcity)
