#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.parse
from time import sleep

import requests
import xmltodict
from dotmap import DotMap

from src.librecatastro.scrapping.scrapper import Scrapper
from src.settings import config
from src.utils.catastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class ScrapperXML(Scrapper):
    """Class that manages the XML scrapping from the Cadastro webservices """

    def __init__(self):
        super().__init__()

    @classmethod
    def scrap_coord(cls, x, y):
        """
        Scraps XML by coordinates
        :param x: Longitude
        :param y: Latitude
        :return: DotMap dictionary with scrapped results
        """
        params = {'SRS': 'EPSG:4326', 'Coordenada_X': x, 'Coordenada_Y': y}
        url = cls.URL_LOCATIONS_BASE.format("/OVCCoordenadas.asmx/Consulta_RCCOOR")
        response = requests.get(url, params=params)

        logger.debug("====Longitude: {} Latitude: {}====".format(x, y))
        logger.debug("URL for coordinates: {}".format(url + '?' + urllib.parse.urlencode(params)))

        xml_dict_map = DotMap(xmltodict.parse(response.content, process_namespaces=False, xml_attribs=False))

        sleep(config['sleep_time'])
        return xml_dict_map

    @classmethod
    def get_cadaster_entries_by_cadaster(cls, prov_name, city_name, cadaster):
        """
        Scraps XML by cadaster, prov_name (optional) and city_name (optional)
        :param prov_name: Name of the province (can be set to '')
        :param city_name: Name of the city (can be set to '')
        :param cadaster: Cadaster code
        :return: DotMap dictionary with scrapped results
        """

        params = {"Provincia": prov_name,
                  "Municipio": city_name,
                  "RC": cadaster}

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/Consulta_DNPRC")
        logger.debug("URL for entry: {}".format(url + '?' + urllib.parse.urlencode(params)))
        response = requests.get(url, params=params)
        xml = response.content

        sleep(config['sleep_time'])
        return DotMap(xmltodict.parse(xml, process_namespaces=False, xml_attribs=False))

    @classmethod
    def get_cadaster_entries_by_address(cls, prov_name, city_name, tv, nv, num, bl=None, es=None,
                                        pl=None, pu=None):
        """
        Scraps XML by address
        :param prov_name: Name of the province (can be set to '')
        :param city_name: Name of the city (can be set to '')
        :param tv: Kind of street (CL - Calle, AV - Avenida, etc)
        :param nv: Name of street
        :param num: Street number
        :param bl: Block (Bloque)
        :param es: Doorway (Escalera)
        :param pl: Floor (Planta)
        :param pu: Door (Puerta)
        :return: DotMap dictionary with scrapped results
        """
        params = {'Provincia': prov_name,
                  'Municipio': city_name,
                  'Sigla': tv,
                  'Calle': nv,
                  'Numero': str(num)}
        if bl:
            params['Bloque'] = str(bl)
        else:
            params['Bloque'] = ''
        if es:
            params['Escalera'] = es
        else:
            params['Escalera'] = ''
        if pl:
            params['Planta'] = str(pl)
        else:
            params['Planta'] = ''
        if pu:
            params['Puerta'] = str(pu)
        else:
            params['Puerta'] = ''

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/Consulta_DNPLOC")
        logger.debug("URL for entry: {}".format(url + '?' + urllib.parse.urlencode(params)))

        response = requests.get(url, params=params)
        xml = response.content

        sleep(config['sleep_time'])
        return DotMap(xmltodict.parse(xml, process_namespaces=False, xml_attribs=False))