import os
import random
import re
import time
import urllib
from urllib import error

from time import sleep
from urllib.request import urlopen
from xml.etree import ElementTree
from bs4 import BeautifulSoup

from src.librecatastro.domain.cadaster_entry.cadaster_entry_html import CadasterEntryHTML
from src.librecatastro.domain.geometry.geo_polygon import GeoPolygon
from src.librecatastro.scrapping.scrapper import Scrapper
from src.settings import config

from src.utils.cadastro_logger import CadastroLogger
from src.utils.list_utils import ListUtils

'''Logger'''
logger = CadastroLogger(__name__).logger


class ScrapperHTML(Scrapper):
    """Scrapper class for Catastro HTML"""

    def __init__(self):
        super().__init__()

    """ Scrapping main calls """

    @classmethod
    def scrap_all_coordinates_files(cls, filenames):
        for r, d, files in os.walk(config['coordinates_path']):
            for file in files:

                if len(filenames) > 0 and file not in filenames:
                    continue

                if '.json' not in file:
                    continue

                try:
                    polygon = GeoPolygon(os.path.join(config['coordinates_path'], file))
                    ScrapperHTML.scrap_polygon(polygon)
                except:
                    logger.error("{} is not formatted properly. Please take a look at the examples.".format(file))

    @staticmethod
    def scrap_polygon(polygon):
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

                    cadaster_list = ScrapperHTML.scrap_coord(x_scaled, y_scaled)

                    for cadaster in cadaster_list:
                        cadaster.to_elasticsearch()

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
    def scrap_results_by_time(seconds, lon_min, lon_max, lat_min, lat_max):
        start_time = time.time()
        results = []

        finished = False
        for x in range(lon_min, lon_max):
            for y in range(lat_min, lat_max):

                x_scaled = x / config['scale']
                y_scaled = y / config['scale']

                try:
                    result = ScrapperHTML.scrap_coord(x_scaled, y_scaled)

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
    def scrap_results_linear_x_times(times, lon_min, lon_max, lat_min, lat_max):
        results = []
        counter = times

        finished = False
        for x in range(lon_min, lon_max):
            for y in range(lat_min, lat_max):

                x_scaled = x / config['scale']
                y_scaled = y / config['scale']

                try:

                    result = ScrapperHTML.scrap_coord(x_scaled, y_scaled)

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
    def scrap_results_random_x_times(times, lon_min, lon_max, lat_min, lat_max):
        results = []
        counter = times
        while counter > 0:
            x = random.randrange(lon_min, lon_max)
            y = random.randrange(lat_min, lat_max)

            x_scaled = x / config['scale']
            y_scaled = y / config['scale']

            try:
                cadaster_entry = ScrapperHTML.scrap_coord(x_scaled, y_scaled)

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

    @staticmethod
    def scrap_coord(x, y):
        logger.debug("====Longitude: {} Latitude: {}====".format(x, y))
        url = Scrapper.URL.format(x, y)
        logger.debug("[|||        ] URL for coordinates: {}".format(url))
        f = urlopen(url)
        data = f.read()
        root = ElementTree.fromstring(data)
        pc1 = root.find("{http://www.catastro.meh.es/}coordenadas//{http://www.catastro.meh.es/}coord//{http://www.catastro.meh.es/}pc//{http://www.catastro.meh.es/}pc1")
        pc2 = root.find("{http://www.catastro.meh.es/}coordenadas//{http://www.catastro.meh.es/}coord//{http://www.catastro.meh.es/}pc//{http://www.catastro.meh.es/}pc2")
        if pc1 is None or pc2 is None:
            return []
        else:
            logger.debug("|||||       ] FOUND!")
            cadaster = ''.join([pc1.text,pc2.text])
            return ScrapperHTML.scrap_cadaster(cadaster, x, y)


    """ Scrapping secondary calls """

    @classmethod
    def parse_html_parcela(cls, parsed_html, x=None, y=None):
        description = parsed_html.find(id='ctl00_Contenido_tblInmueble')

        descriptive_data = dict()
        descriptive_data[u'Longitud'] = x
        descriptive_data[u'Latitud'] = y
        descriptive_data[u'Construcciones'] = []


        ''' Datos descriptivos and Parcela Catastral '''
        fields = description.find_all('div')
        for field in fields:
            field_header = field.find('span')
            for field_name in cls.description_field_names:
                if field_name in field_header.text:
                    field_value = field.find('label', {"class": "control-label black text-left"})
                    descriptive_data[field_name] = field_value.text.strip()

                    if field_header.text == u'Referencia catastral':
                        descriptive_data[field_name] = descriptive_data[field_name].split(' ')[0]
                        descriptive_data[field_name] = descriptive_data[field_name].split('\xa0')[0]
                    elif field_header.text == u'Localización':
                        descriptive_data[field_name] = field_value.encode_contents().decode('utf-8').replace('<br/>', config['separator']).replace('<br>', config['separator'])

        '''Graphical Surface'''
        fields = parsed_html.find(id='ctl00_Contenido_tblFinca').find_all('div')
        for field in fields:
            field_header = field.find('span')
            for field_name in cls.gsurface_field_names:
                if field_name in field_header.text:
                    field_value = field.find('label', {"class": "control-label black text-left"})
                    descriptive_data[field_name] = field_value.text.strip()

        '''Constructions'''
        constructions_table = parsed_html.find(id='ctl00_Contenido_tblLocales');
        if constructions_table is None:
            constructions = []
        else:
            constructions = constructions_table.find_all('tr')
        header = True
        for construction in constructions:
            if header:
                header = False
                continue
            columns = construction.find_all('span')

            descriptive_data[u'Construcciones'].append(dict(uso=columns[0].text, escalera=columns[1].text, planta=columns[2].text, puerta=columns[3].text, superficie=columns[4].text, tipo=columns[5].text, fecha=columns[6].text))

        cadaster_entry = CadasterEntryHTML(descriptive_data)
        return cadaster_entry

    @classmethod
    def scrap_cadaster_full_code(cls, full_cadaster, delimitacion, municipio, x=None, y=None):
        url_ref = cls.URL_REF_FULL.format(full_cadaster, full_cadaster, delimitacion, municipio)
        logger.debug("-->FULL URL for cadastral data: {}".format(url_ref))
        f_ref = urlopen(url_ref)
        data_ref = f_ref.read()
        html = str(data_ref.decode('utf-8'))
        parsed_html = BeautifulSoup(html, features="html.parser")
        return ScrapperHTML.parse_html_parcela(parsed_html, x, y)

    @classmethod
    def scrap_cadaster(cls, cadaster, x=None, y=None):
        rc_1 = cadaster[0:7]
        rc_2 = cadaster[7:14]
        url_ref = cls.URL_REF.format(rc_1, rc_2)

        logger.debug("[||||||||   ] URL for cadastral data: {}".format(url_ref))

        f_ref = urlopen(url_ref)
        data_ref = f_ref.read()
        html = str(data_ref.decode('utf-8'))
        parsed_html = BeautifulSoup(html, features="html.parser")

        delimitacion = ''
        delimitacion_search = re.search(r'del=([0-9]+)&', html)
        if delimitacion_search:
            delimitacion = delimitacion_search.group(1)

        municipio = ''
        municipio_search = re.search(r'mun=([0-9]+)&', html)
        if municipio_search:
            municipio = municipio_search.group(1)

        description = parsed_html.find(id='ctl00_Contenido_tblInmueble')

        cadasters = []
        if description is None:
            logger.debug("Multiparcela found!")
            ''' Multiparcela with multiple cadasters '''

            all_cadasters = parsed_html.findAll("div", {"id": re.compile('heading[0-9]+')})
            logger.debug("->Parcelas found: {}".format(len(all_cadasters)))
            for partial_cadaster in all_cadasters:
                partial_cadaster_ref = partial_cadaster.find("b")
                logger.debug("-->Partial cadaster: {}".format(partial_cadaster_ref.text))
                partial_cadaster_text = partial_cadaster_ref.text.strip()
                cadaster = ScrapperHTML.scrap_cadaster_full_code(partial_cadaster_text, delimitacion, municipio,
                                                                        x, y)
                cadasters.append(cadaster)
        else:
            cadaster = ScrapperHTML.parse_html_parcela(parsed_html, x, y)
            cadasters.append(cadaster)

        logger.debug("[|||||||||||] SUCCESS!")
        return cadasters
