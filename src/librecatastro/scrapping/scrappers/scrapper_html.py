#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from time import sleep
from urllib.request import urlopen

from bs4 import BeautifulSoup

from src.librecatastro.scrapping.scrapper import Scrapper
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class ScrapperHTML(Scrapper):
    """Class that manages the HTML scrapping from the Cadastro Official Page """

    ''' Some reference URLs'''
    URL = "http://ovc.catastro.meh.es/ovcservweb/ovcswlocalizacionrc/ovccoordenadas.asmx/Consulta_RCCOOR?SRS=EPSG:4326&Coordenada_X={}&Coordenada_Y={}"
    URL_REF = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCListaBienes.aspx?rc1={}&rc2={}"
    URL_REF_FULL = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?RefC={}&RCCompleta={}&del={}&mun={}"

    def __init__(self):
        super().__init__()

    @classmethod
    def scrap_coord(cls, x, y):
        """
        Scraps HTML by coordinates
        :param x: Longitude
        :param y: Latitude
        :return: HTML content of the cadaster entry
        """
        logger.debug("====Longitude: {} Latitude: {}====".format(x, y))
        url = cls.URL.format(x, y)
        logger.debug("URL for coordinates: {}".format(url))
        f = urlopen(url)

        sleep(config['sleep_time'])
        return f.read()

    @classmethod
    def scrap_cadaster_full_code(cls, full_cadaster, prov_num, city_num):
        """
        Scraps HTML by cadaster full code, province (delimitacion) and city (municipio)
        :param full_cadaster: Full cadaster code (>14 characters)
        :param prov_num: Province number
        :param city_num: City number
        :return: BeautifulSoup-parsed HTML content of the cadaster entry
        """
        url_ref = cls.URL_REF_FULL.format(full_cadaster, full_cadaster, prov_num, city_num)
        logger.debug("-->FULL URL for cadastral data: {}".format(url_ref))
        f_ref = urlopen(url_ref)
        data_ref = f_ref.read()
        html = str(data_ref.decode('utf-8'))
        parsed_html = BeautifulSoup(html, features="html.parser")

        sleep(config['sleep_time'])
        return parsed_html

    @classmethod
    def scrap_cadaster(cls, cadaster, prov_num=None, city_num=None, pictures=False):
        """
        Scraps HTML by cadaster code. This probably will return several entries (Multiparcela), since a non-full cadaster
        belongs to entire buildings. But sometimes it will return just one entry (Parcela) in case of, for example,
        country houses.

        :param cadaster: 14-characters code of a cadaster
        :param prov_num: Province number
        :param city_num: City number
        :param pictures: True if we want to obtain the house plan picture. False otherwise.
        :return: A List of CadasterEntry objects.
        """
        rc_1 = cadaster[0:7]
        rc_2 = cadaster[7:14]
        url_ref = cls.URL_REF.format(rc_1, rc_2)

        logger.debug("URL for cadastral data: {}".format(url_ref))

        f_ref = urlopen(url_ref)
        data_ref = f_ref.read()
        sleep(config['sleep_time'])

        html = str(data_ref.decode('utf-8'))
        parsed_html = BeautifulSoup(html, features="html.parser")

        if prov_num is None:
            delimitacion_search = re.search(r'del=([0-9]+)&', html)
            if delimitacion_search:
                prov_num = delimitacion_search.group(1)

        if city_num is None:
            municipio_search = re.search(r'mun=([0-9]+)&', html)
            if municipio_search:
                city_num = municipio_search.group(1)

        description = parsed_html.find(id='ctl00_Contenido_tblInmueble')

        picture = None
        if pictures:
            picture = cls.scrap_site_picture(prov_num, city_num, ''.join([rc_1, rc_2]))
            sleep(config['sleep_time'])

        htmls = []
        if description is None:
            # Multiparcela
            logger.debug("Multiparcela found!")
            ''' Multiparcela with multiple cadasters '''

            all_cadasters = parsed_html.findAll("div", {"id": re.compile('heading[0-9]+')})
            logger.debug("->Parcelas found: {}".format(len(all_cadasters)))
            for partial_cadaster in all_cadasters:
                partial_cadaster_ref = partial_cadaster.find("b")
                logger.debug("-->Partial cadaster: {}".format(partial_cadaster_ref.text))
                partial_cadaster_text = partial_cadaster_ref.text.strip()
                parsed_html = ScrapperHTML.scrap_cadaster_full_code(partial_cadaster_text, prov_num, city_num)
                htmls.append((parsed_html, picture))
                sleep(config['sleep_time'])
        else:
            # Parcela
            htmls.append((parsed_html, picture))

        return htmls

