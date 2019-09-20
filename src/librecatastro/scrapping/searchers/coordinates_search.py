#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import urllib.error
import random
from time import sleep

from src.librecatastro.domain.geometry.geo_polygon import GeoPolygon
from src.librecatastro.scrapping.search import Search
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger
from src.utils.list_utils import ListUtils

'''Logger'''
logger = CadastroLogger(__name__).logger


class CoordinatesSearch(Search):
    def __init__(self):
        super().__init__()

    @classmethod
    def scrap_coordinates(cls, scrapper, filenames, pictures=False):
        for r, d, files in os.walk(config['coordinates_path']):
            for file in files:

                if len(filenames) > 0 and file not in filenames:
                    continue

                if '.json' not in file:
                    continue

                try:
                    polygon = GeoPolygon(os.path.join(config['coordinates_path'], file))
                    CoordinatesSearch.scrap_polygon(scrapper, polygon, pictures)
                except:
                    logger.error("{} is not formatted properly. Please take a look at the examples.".format(file))

    @classmethod
    def scrap_polygon(cls, scrapper, polygon, pictures=False):
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
                    scrapper.scrap_coord(x_scaled, y_scaled, pictures)

                except urllib.error.HTTPError as e:
                    logger.error("ERROR AT LONGITUDE {} LATITUDE {}".format(x_scaled, y_scaled))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("...sleeping...")
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
    def scrap_results_by_time(seconds, lon_min, lon_max, lat_min, lat_max, scrapper):
        start_time = time.time()
        results = []

        finished = False
        for x in range(lon_min, lon_max):
            for y in range(lat_min, lat_max):

                x_scaled = x / config['scale']
                y_scaled = y / config['scale']

                try:
                    result = scrapper.scrap_coord(x_scaled, y_scaled)

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
    def scrap_results_linear_x_times(times, lon_min, lon_max, lat_min, lat_max, scrapper):
        results = []
        counter = times

        finished = False
        for x in range(lon_min, lon_max):
            for y in range(lat_min, lat_max):

                x_scaled = x / config['scale']
                y_scaled = y / config['scale']

                try:

                    result = scrapper.scrap_coord(x_scaled, y_scaled)

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
    def scrap_results_random_x_times(times, lon_min, lon_max, lat_min, lat_max, scrapper):
        results = []
        counter = times
        while counter > 0:
            x = random.randrange(lon_min, lon_max)
            y = random.randrange(lat_min, lat_max)

            x_scaled = x / config['scale']
            y_scaled = y / config['scale']

            try:
                cadaster_entry = scrapper.scrap_coord(x_scaled, y_scaled)

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
        logger.debug("Results found: {}".format(times))
        return ListUtils.flat(results)
