#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import urllib.error
import random
from time import sleep

from src.librecatastro.domain.geometry.geo_polygon import GeoPolygon
from src.librecatastro.scrapping.searcher import Searcher
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger
from src.utils.list_utils import ListUtils

'''Logger'''
logger = CadastroLogger(__name__).logger


class CoordinatesSearcher(Searcher):
    """
    Class that inheritates from Searcher Abstract Class and implements
    functions regarding coordinates search.
    """
    def __init__(self):
        super().__init__()

    @classmethod
    def search_by_coordinates(cls, scrapper, filenames, pictures=False):
        """
        Function that searches Cadastro (HTML or XML) by coordinates
        :param scrapper: HTMLScrapper or XMLScrapper classes
        :param filenames: Names of the filenames with coordinates to scrap
        :param pictures: Do we want to scrap house plan pictures?

        """
        for r, d, files in os.walk(config['coordinates_path']):
            for file in files:

                if len(filenames) > 0 and file not in filenames:
                    continue

                if '.json' not in file:
                    continue

                try:
                    polygon = GeoPolygon(os.path.join(config['coordinates_path'], file))
                    CoordinatesSearcher.search_in_polygon(scrapper, polygon, pictures)
                except:
                    logger.error("{} is not formatted properly. Please take a look at the examples.".format(file))

    @classmethod
    def search_in_polygon(cls, scrapper, polygon, pictures=False):
        """
        Function that searchs by coordinates strictly inside a Polygon
        defined by the user.

        :param scrapper: HTMLScrapper or XMLScrapper classes
        :param polygon: a GeoPolygon class object
        :param pictures: Do we want to scrap house plan pictures?
        """
        bb = polygon.get_bounding_box()
        lon_min = int(bb[0] * config['scale'])
        lon_max = int(bb[2] * config['scale'])
        lat_min = int(bb[1] * config['scale'])
        lat_max = int(bb[3] * config['scale'])
        for x in range(lon_min, lon_max):
            for y in range(lat_min, lat_max):

                x_scaled = x / config['scale']
                y_scaled = y / config['scale']
                if not polygon.is_point_in_polygon(x_scaled, y_scaled):
                    continue

                ''' Adding to tracking file'''
                logger.info('{},{}'.format(x_scaled, y_scaled))

                try:
                    scrapper.process_search_by_coordinates(x_scaled, y_scaled, pictures)

                except urllib.error.HTTPError as e:
                    logger.error("ERROR AT LONGITUDE {} LATITUDE {}".format(x_scaled, y_scaled))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("...sleeping due to connection reset...")
                    logger.debug("...sleeping due to connection reset...")
                    logger.error("=============================================")
                    ''' Could be a service Unavailable or denegation of service'''
                    sleep(config['sleep_dos_time'])
                except Exception as e:
                    logger.error("ERROR AT LONGITUDE {} LATITUDE {}".format(x_scaled, y_scaled))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("=============================================")

                sleep(config['sleep_time'])

    @staticmethod
    def search_by_coordinates_max_time(seconds, lon_min, lon_max, lat_min, lat_max, scrapper):
        """
        Function that allows searching in lon, lat for a maximum number of seconds.
        Mainly used for debugging purposes.

        :param seconds: Total of seconds to scrap
        :param lon_min: Minimum longitude
        :param lon_max: Maximum longitude
        :param lat_min: Minimum latitude
        :param lat_max: Maximum latitude
        :param scrapper: HTML or XML Scrapper
        :return: a List of CadasterEntry objects
        """
        start_time = time.time()
        results = []

        finished = False
        for x in range(lon_min, lon_max):
            for y in range(lat_min, lat_max):

                x_scaled = x / config['scale']
                y_scaled = y / config['scale']

                try:
                    result = scrapper.process_search_by_coordinates(x_scaled, y_scaled)

                    if result is not None:
                        results.append(result)
                        now = time.time()
                        elapsed_time = now - start_time
                        if elapsed_time > seconds:
                            finished = True
                            break

                except urllib.error.HTTPError as e:
                    logger.error("ERROR AT LONGITUDE {} LATITUDE {}".format(x_scaled, y_scaled))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("=============================================")
                    ''' Could be a service Unavailable or denegation of service'''
                    sleep(config['sleep_dos_time'])
                except Exception as e:
                    logger.error("ERROR AT LONGITUDE {} LATITUDE {}".format(x_scaled, y_scaled))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("=============================================")
                sleep(config['sleep_time'])

            if finished:
                break
        return ListUtils.flat(results)

    @staticmethod
    def search_by_coordinates_linear_max_n_matches(matches, lon_min, lon_max, lat_min, lat_max, scrapper):
        """
            Function that allows searching in lon, lat for a maximum number of matches.
            Mainly used for debugging purposes.

            :param matches: Total of matches to scrap
            :param lon_min: Minimum longitude
            :param lon_max: Maximum longitude
            :param lat_min: Minimum latitude
            :param lat_max: Maximum latitude
            :param scrapper: HTML or XML Scrapper
            :return: a List of CadasterEntry objects
        """
        results = []
        counter = matches

        finished = False
        for x in range(lon_min, lon_max):
            for y in range(lat_min, lat_max):

                x_scaled = x / config['scale']
                y_scaled = y / config['scale']

                try:

                    result = scrapper.process_search_by_coordinates(x_scaled, y_scaled)

                    if result is not None:
                        results.append(result)
                        counter -= 1
                        if counter == 0:
                            finished = True
                            break

                except urllib.error.HTTPError as e:
                    logger.error("ERROR AT LONGITUDE {} LATITUDE {}".format(x_scaled, y_scaled))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("=============================================")
                    ''' Could be a service Unavailable or denegation of service'''
                    sleep(config['sleep_dos_time'])
                except Exception as e:
                    logger.error("ERROR AT LONGITUDE {} LATITUDE {}".format(x_scaled, y_scaled))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("=============================================")
                sleep(config['sleep_time'])

            if finished:
                break

        return ListUtils.flat(results)

    @staticmethod
    def search_by_coordinates_random_max_n_matches(matches, lon_min, lon_max, lat_min, lat_max, scrapper):
        """
            Function that allows searching in lon, lat for a maximum number of matches.
            Mainly used for debugging purposes.

            :param matches: Total of matches to scrap
            :param lon_min: Minimum longitude
            :param lon_max: Maximum longitude
            :param lat_min: Minimum latitude
            :param lat_max: Maximum latitude
            :param scrapper: HTML or XML Scrapper
            :return: a List of CadasterEntry objects
        """
        results = []
        counter = matches
        while counter > 0:

            x = random.randrange(lon_min, lon_max)
            y = random.randrange(lat_min, lat_max)

            x_scaled = x / config['scale']
            y_scaled = y / config['scale']

            try:
                cadaster_entry = scrapper.process_search_by_coordinates(x_scaled, y_scaled)

                if len(cadaster_entry) > 0:
                    results.append(cadaster_entry)
                    counter -= 1
                    if counter == 0:
                        break
            except urllib.error.HTTPError as e:
                logger.error("ERROR AT LONGITUDE {} LATITUDE {}".format(x_scaled, y_scaled))
                logger.error("=============================================")
                logger.error(e, exc_info=True)
                logger.error("=============================================")
                ''' Could be a service Unavailable or denegation of service'''
                sleep(config['sleep_dos_time'])
            except Exception as e:
                logger.error("ERROR AT LONGITUDE {} LATITUDE {}".format(x_scaled, y_scaled))
                logger.error("=============================================")
                logger.error(e, exc_info=True)
                logger.error("=============================================")
            sleep(config['sleep_time'])

        logger.debug("====PROCESSING FINISHED====")
        logger.debug("Results found: {}".format(matches))
        return ListUtils.flat(results)
