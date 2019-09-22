import urllib.parse
from time import sleep

import requests
import xmltodict
from dotmap import DotMap

from src.librecatastro.scrapping.scrapper import Scrapper
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class ScrapperXML(Scrapper):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_coord(cls,x, y):
        params = {'SRS': 'EPSG:4326', 'Coordenada_X': x, 'Coordenada_Y': y}
        url = cls.URL_LOCATIONS_BASE.format("/OVCCoordenadas.asmx/Consulta_RCCOOR")
        response = requests.get(url, params=params)

        logger.debug("====Longitude: {} Latitude: {}====".format(x, y))
        logger.debug("URL for coordinates: {}".format(url + '?' + urllib.parse.urlencode(params)))

        xml_dict_map = DotMap(xmltodict.parse(response.content, process_namespaces=False, xml_attribs=False))

        sleep(config['sleep_time'])
        return xml_dict_map

    @classmethod
    def get_cadaster_entries_by_cadaster(cls, provincia, municipio, rc):
        """ provincia and municipio are optional and can be set to '' """

        params = {"Provincia": provincia,
                  "Municipio": municipio,
                  "RC": rc}

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/Consulta_DNPRC")
        logger.debug("URL for entry: {}".format(url + '?' + urllib.parse.urlencode(params)))
        response = requests.get(url, params=params)
        xml = response.content

        sleep(config['sleep_time'])
        return DotMap(xmltodict.parse(xml, process_namespaces=False, xml_attribs=False))

    @classmethod
    def get_cadaster_entries_by_address(cls, provincia, municipio, sigla, calle, numero, bloque=None, escalera=None,
                                        planta=None,puerta=None):
        params = {'Provincia': provincia,
                  'Municipio': municipio,
                  'Sigla': sigla,
                  'Calle': calle,
                  'Numero': str(numero)}
        if bloque:
            params['Bloque'] = str(bloque)
        else:
            params['Bloque'] = ''
        if escalera:
            params['Escalera'] = escalera
        else:
            params['Escalera'] = ''
        if planta:
            params['Planta'] = str(planta)
        else:
            params['Planta'] = ''
        if puerta:
            params['Puerta'] = str(puerta)
        else:
            params['Puerta'] = ''

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/Consulta_DNPLOC")
        logger.debug("URL for entry: {}".format(url + '?' + urllib.parse.urlencode(params)))

        response = requests.get(url, params=params)
        xml = response.content

        sleep(config['sleep_time'])
        return DotMap(xmltodict.parse(xml, process_namespaces=False, xml_attribs=False))