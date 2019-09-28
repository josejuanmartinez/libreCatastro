#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.error
from time import sleep

from xml.etree import ElementTree
from dotmap import DotMap

from src.librecatastro.domain.cadaster_entry.cadaster_entry_html import CadasterEntryHTML
from src.librecatastro.scrapping.parser import Parser
from src.librecatastro.scrapping.scrapper import Scrapper
from src.librecatastro.scrapping.scrappers.scrapper_html import ScrapperHTML
from src.settings import config

from src.utils.cadastro_logger import CadastroLogger
from src.utils.elasticsearch_utils import ElasticSearchUtils

'''Logger'''
logger = CadastroLogger(__name__).logger


class ParserHTML(Parser):
    """Class that manages the processing of scrapped HTML from Cadastro webpage"""

    def __init__(self):
        super().__init__()

    '''Information to scrap from HTML'''
    description_field_names = [u'Referencia catastral', u'Localización', u'Clase', u'Uso principal',
                               u'Superficie construida', u'Año construcción']

    gsurface_field_names = [u'Superficie gráfica']

    """ Processing """
    @classmethod
    def process_search_by_coordinates(cls, x, y, pictures=False):
        """
        Searches by coordinate from HTML and processes the result.
        :param x: longitude
        :param y: latitude
        :param pictures: True if we want house plan pictures to be scrapped
        :return: List of CadasterEntry objects
        """
        data = ScrapperHTML.scrap_coord(x, y)

        root = ElementTree.fromstring(data)
        pc1 = root.find(
            "{http://www.catastro.meh.es/}coordenadas//{http://www.catastro.meh.es/}coord//{http://www.catastro.meh.es/}pc//{http://www.catastro.meh.es/}pc1")
        pc2 = root.find(
            "{http://www.catastro.meh.es/}coordenadas//{http://www.catastro.meh.es/}coord//{http://www.catastro.meh.es/}pc//{http://www.catastro.meh.es/}pc2")

        results = []
        if pc1 is not None and pc2 is not None:
            cadaster = ''.join([pc1.text, pc2.text])
            html_picture_tuples = ScrapperHTML.scrap_cadaster(cadaster, None, None, pictures)

            if not isinstance(html_picture_tuples, list):
                html_picture_tuples = [html_picture_tuples]

            for html_picture_tuple in html_picture_tuples:
                html, picture = html_picture_tuple
                cadaster_entry = cls.parse_html_parcela(html, x, y, picture)
                cadaster_entry.to_elasticsearch()
                results.append(cadaster_entry)

        return results

    @classmethod
    def process_search_by_provinces(cls, prov_list, pictures=False, start_from='', matches=None):
        """
            Searches by province from HTML and processes the result.
            :param prov_list: List of province names
            :param start_from: Name of the city of the first province to start from
            :param pictures: True if we want house plan pictures to be scrapped
            :param matches: Max number of matches (for debugging purporses mainly)
            :return: List of CadasterEntry objects
        """
        times = 0
        results = []

        num = ''
        for prov_name, prov_num, city_name, city_num, address, tv, nv in Scrapper.get_address_iter(prov_list, start_from):

            if tv == DotMap() or nv == DotMap():
                continue

            if ElasticSearchUtils.check_if_address_present("{} {}".format(tv, nv), city_name, prov_name):
                logger.debug("Skipping {} {} {} {} because it's been already scrapped.".format(tv, nv,
                                                                                               prov_name, city_name))
                continue

            num_scrapping_fails = 10
            counter = 1
            while num_scrapping_fails > 0:
                try:
                    numerero_map = Scrapper.get_cadaster_by_address(prov_name, city_name, tv, nv, counter)
                    if numerero_map.consulta_numerero.lerr.err.cod != DotMap():
                        num_scrapping_fails -= 1
                    else:

                        numps = numerero_map.consulta_numerero.numerero.nump

                        if not isinstance(numps, list):
                            numps = [numps]

                        for nump in numps:
                            if nump.num.pnp == DotMap():
                                continue

                            num = nump.num.pnp

                            if nump.pc == DotMap():
                                continue

                            if nump.pc.pc1 == DotMap() or nump.pc.pc2 == DotMap():
                                continue

                            cadaster_num = nump.pc.pc1 + nump.pc.pc2

                            coords_map = Scrapper.get_coords_from_cadaster(prov_name, city_name, cadaster_num)

                            lon = coords_map.consulta_coordenadas.coordenadas.coord.geo.xcen
                            if lon == DotMap():
                                lon = None

                            lat = coords_map.consulta_coordenadas.coordenadas.coord.geo.ycen
                            if lat == DotMap():
                                lat = None

                            ''' Adding to tracking file'''
                            logger.info('{},{}'.format(lon, lat))

                            num_scrapping_fails = 10

                            htmls = ScrapperHTML.scrap_cadaster(cadaster_num, prov_num, city_num, pictures)

                            for html, picture in htmls:
                                cadaster_entry = cls.parse_html_parcela(html, lon, lat, picture)
                                cadaster_entry.to_elasticsearch()
                                results.append(cadaster_entry)

                        counter += 1
                        times += 1

                        if matches is not None and times >= matches:
                            return results

                except urllib.error.HTTPError as e:
                    logger.error(
                        "ERROR AT ADDRESS {} {} {} {} {}".format(tv, nv, num, prov_name, city_name))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("...sleeping due to connection reset...")
                    logger.debug("...sleeping due to connection reset...")
                    logger.error("=============================================")
                    ''' Could be a service Unavailable or denegation of service'''
                    num_scrapping_fails -= 1
                    sleep(config['sleep_dos_time'])

                except Exception as e:
                    logger.error(
                        "ERROR AT ADDRESS {} {} {} {} {}".format(tv, nv, num, prov_name, city_name))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("=============================================")
                    num_scrapping_fails -= 1

                counter += 1

    """ Parsing """
    @classmethod
    def parse_html_parcela(cls, parsed_html, x=None, y=None, picture=None):
        """
            Parses an HTML and crates a CadasterEntry object
            :param x: longitude obtained previously
            :param y: latitude obtained previously
            :param pictures: base64 picture obtained previously
            :return: CadasterEntry object
        """
        description = parsed_html.find(id='ctl00_Contenido_tblInmueble')

        descriptive_data = dict()
        descriptive_data[u'Longitud'] = x
        descriptive_data[u'Latitud'] = y
        descriptive_data[u'GráficoParcela'] = picture
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
                        descriptive_data[field_name] = field_value.encode_contents().decode('utf-8').replace('<br/>',config['separator']).replace('<br>', config['separator'])

        '''Graphical Surface'''
        fields = parsed_html.find(id='ctl00_Contenido_tblFinca').find_all('div')
        for field in fields:
            field_header = field.find('span')
            for field_name in cls.gsurface_field_names:
                if field_name in field_header.text:
                    field_value = field.find('label', {"class": "control-label black text-left"})
                    descriptive_data[field_name] = field_value.text.strip()

        '''Constructions'''
        constructions_table = parsed_html.find(id='ctl00_Contenido_tblLocales')
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

            descriptive_data[u'Construcciones'].append(
                dict(uso=columns[0].text, escalera=columns[1].text, planta=columns[2].text, puerta=columns[3].text,
                     superficie=columns[4].text, tipo=columns[5].text, fecha=columns[6].text))

        descriptive_data[u'GráficoParcela']=picture
        cadaster_entry = CadasterEntryHTML(descriptive_data)
        return cadaster_entry
