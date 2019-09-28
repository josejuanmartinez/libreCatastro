#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
from time import sleep
from urllib.request import urlopen
import urllib.parse

import requests
import xmltodict
from dotmap import DotMap

from src.settings import config
from src.utils.catastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class Scrapper:
    """Scrapper class, from which inheritates ScrapperHTML and ScrapperXML, and which
    implements common scrapping functions for both HTML and XML"""

    '''libreCatastro web services parametrized'''

    URL_PICTURES = "https://www1.sedecatastro.gob.es/Cartografia/GeneraGraficoParcela.aspx?del={}&mun={}&refcat={}&AnchoPixels={}&AltoPixels={}"
    URL_LOCATIONS_BASE = "http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC{}"

    def __init__(self):
        pass

    @classmethod
    def get_provinces(cls):
        """Get all provinces registered by libreCatastro (call only available from XML but used in both XML and HTML)"""

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/ConsultaProvincia")
        response = requests.get(url)
        xml = response.content

        sleep(config['sleep_time'])
        return DotMap(xmltodict.parse(xml, process_namespaces=False, xml_attribs=False))

    @classmethod
    def get_cities(cls, prov_name, city_name=None):
        """
        Get all cities registered by libreCatastro (call only available from XML but used in both XML and HTML)
        :param prov_name: Name of the province (from Cadaster Province List)
        :param city_name: Optional. Name of the city (from Cadaster City List) in case a specific city is required
        :return: DotMap (dict with properties accessible by '.') with all the cities
        """
        params = {'Provincia': prov_name}
        if city_name:
            params['Municipio'] = city_name
        else:
            params['Municipio'] = ''
        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/ConsultaMunicipio")
        response = requests.get(url, params=params)
        xml = response.content

        sleep(config['sleep_time'])
        return DotMap(xmltodict.parse(xml, process_namespaces=False, xml_attribs=False))

    @classmethod
    def get_addresses(cls, prov_name, city_name, tv=None, nv=None):
        """
        Get all addresses registered by libreCatastro (call only available from XML but used in both XML and HTML)

        :param prov_name: Name of the province (from Cadaster Province List)
        :param city_name: Name of the city (from Cadaster City List)
        :param tv: Optional. Name of the kind of street (CL, AV ...) in case a specific kind is needed
        :param nv: Optional. Name of the street in case a specific street is needed
        :return: DotMap (dict with properties accessible by '.') with all the cities
        """

        params = {'Provincia': prov_name,
                  'Municipio': city_name}
        if tv:
            params['TipoVia'] = tv
        else:
            params['TipoVia'] = ''
        if nv:
            params['NombreVia'] = nv
        else:
            params['NombreVia'] = ''

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/ConsultaVia")
        response = requests.get(url, params=params)
        xml = response.content

        sleep(config['sleep_time'])
        return DotMap(xmltodict.parse(xml, process_namespaces=False, xml_attribs=False))

    @classmethod
    def get_address_iter(cls, prov_list=None, start_from=''):
        """
        Funcion that, instead of returning all the addresses, returns an iterator to all the addresses of a province list
        to optimize performance.

        :param prov_list: List of province names to get addresses from (from Cadaster Province List)
        :param start_from: Optional. Name of the city where to start from in a province (from Cadaster City List)
        :return: iterator to all the addresses of the provinces of the list
        """
        if prov_list is None:
            prov_list = []

        provinces = cls.get_provinces().consulta_provinciero.provinciero.prov
        if provinces == DotMap():
            logger.error("No provinces available right now (Service is down?)")
            yield None

        for province in provinces:
            prov_name = province.np
            prov_num = province.cpine
            if prov_name == DotMap() or prov_num == DotMap():
                continue

            if len(prov_list) > 0 and prov_name not in prov_list:
                continue

            cities = cls.get_cities(prov_name).consulta_municipiero.municipiero.muni
            if cities == DotMap():
                logger.error("No cities available right now (Service is down?)")
                return

            for city in cities:
                city_name = city.nm
                city_num = city.locat.cmc

                if city_name == DotMap() or city_num == DotMap():
                    continue

                if start_from != '' and city_name != start_from:
                    logger.debug("Skipping {}".format(city_name))
                    continue

                addresses = cls.get_addresses(prov_name, city_name).consulta_callejero.callejero.calle
                if addresses == DotMap():
                    logger.error("No addresses available right now (Service is down?)")
                    return

                for address in addresses:

                    address_dir = address.dir
                    tv = address_dir.tv
                    nv = address_dir.nv

                    if tv == DotMap() or nv == DotMap():
                        continue
                    else:
                        yield (prov_name, prov_num, city_name, city_num, address_dir, tv, nv)

    @classmethod
    def scrap_site_picture(cls, prov_num, city_num, cadaster):
        """
        Gets the house plan picture.

        :param prov_num: Province number.
        :param city_num: City number.
        :param cadaster: Cadaster number.
        :return: an image, coded in base64.
        """

        url_pic = cls.URL_PICTURES.format(prov_num, city_num, cadaster, config['width_px'], config['height_px'])

        logger.debug("URL for picture data: {}".format(url_pic))

        f_pic = urlopen(url_pic)

        data_ref = f_pic.read()

        b64_image = base64.b64encode(data_ref).decode('utf-8')

        sleep(config['sleep_time'])
        return b64_image

    @classmethod
    def get_cadaster_by_address(cls, prov_name, city_name, tv, nv, num):
        """
        Gets the cadaster information, based on an address.

        :param prov_name: Name of the province.
        :param city_name: Name of the city.
        :param tv: Kind of street (CL, AV...)
        :param nv: Name of the street
        :param num: Number of the street
        :return: DotMap (dict with properties accessible by '.') with the cadaster information
        """
        params = {'Provincia': prov_name,
                  'Municipio': city_name,
                  'TipoVia': tv,
                  'NomVia': nv,
                  'Numero': str(num)}

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/ConsultaNumero")

        logger.debug("====Dir: {} {} {} {} {}====".format(tv, nv, num, city_name, prov_name))
        logger.debug("URL for address: {}".format(url + '?' + urllib.parse.urlencode(params)))

        response = requests.get(url, params=params)
        xml = response.content

        sleep(config['sleep_time'])
        return DotMap(xmltodict.parse(xml, process_namespaces=False, xml_attribs=False))

    @classmethod
    def get_coords_from_cadaster(cls, prov_name, city_name, cadaster):
        """
        Returns the lon (xcen) and lat (ycen) of a property, identified by its cadaster number
        and province and city names.

        :param prov_name: Province name.
        :param city_name: City name.
        :param cadaster: Cadaster number.
        :return: DotMap (dict with properties accessible by '.') with the location information
        """
        params = {'Provincia': prov_name, 'Municipio': city_name, 'SRS': 'EPSG:4326', 'RC': cadaster}
        url = cls.URL_LOCATIONS_BASE.format("/OVCCoordenadas.asmx/Consulta_CPMRC")

        logger.debug("URL for coordinates: {}".format(url + '?' + urllib.parse.urlencode(params)))

        response = requests.get(url, params=params)
        xml = response.content

        sleep(config['sleep_time'])
        return DotMap(xmltodict.parse(xml, process_namespaces=False, xml_attribs=False))

