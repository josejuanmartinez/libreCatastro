import urllib.parse

import requests
import xmltodict

from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class Scrapper:
    """Generic Scrapper class"""

    '''Catastro web services parametrized'''
    URL_LOCATIONS_BASE = "http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC{}"

    def __init__(self):
        pass

    @classmethod
    def scrap_coords(cls, x, y):
        pass

    @classmethod
    def scrap_provinces(cls, prov_list):
        pass

    @classmethod
    def get_provinces(cls):
        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/ConsultaProvincia")
        response = requests.get(url)
        xml = response.content
        return xmltodict.parse(xml, process_namespaces=False, xml_attribs=False)

    @classmethod
    def get_cities(cls, provincia, municipio=None):
        params = {'Provincia': provincia}
        if municipio:
            params['Municipio'] = municipio
        else:
            params['Municipio'] = ''
        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/ConsultaMunicipio")
        response = requests.get(url, params=params)
        xml = response.content
        return xmltodict.parse(xml, process_namespaces=False, xml_attribs=False)

    @classmethod
    def get_addresses(cls, provincia, municipio, tipovia=None, nombrevia=None):
        params = {'Provincia': provincia,
                  'Municipio': municipio}
        if tipovia:
            params['TipoVia'] = tipovia
        else:
            params['TipoVia'] = ''
        if nombrevia:
            params['NombreVia'] = nombrevia
        else:
            params['NombreVia'] = ''

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/ConsultaVia")
        response = requests.get(url, params=params)
        xml = response.content
        return xmltodict.parse(xml, process_namespaces=False, xml_attribs=False)

    @classmethod
    def get_cadaster_by_address(cls, provincia, municipio, tipovia, nombrevia, numero):
        params = {'Provincia': provincia,
                  'Municipio': municipio,
                  'TipoVia': tipovia,
                  'NomVia': nombrevia,
                  'Numero': str(numero)}

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/ConsultaNumero")

        logger.debug("====Dir: {} {} {} {} {}====".format(tipovia, nombrevia, numero, municipio, provincia))
        logger.debug("[|||        ] URL for address: {}".format(url + '?' + urllib.parse.urlencode(params)))

        response = requests.get(url, params=params)
        xml = response.content
        return xmltodict.parse(xml, process_namespaces=False, xml_attribs=False)

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
        logger.debug("[|||||||||| ] URL for entry: {}".format(url + '?' + urllib.parse.urlencode(params)))

        response = requests.get(url, params=params)
        xml = response.content
        return xmltodict.parse(xml, process_namespaces=False, xml_attribs=False)

    @classmethod
    def get_cadaster_entries_by_cadaster(cls, provincia, municipio, rc):
        """ provincia and municipio are optional and can be set to ''"""
        params = {"Provincia": provincia,
                  "Municipio": municipio,
                  "RC": rc}

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/Consulta_DNPRC")
        logger.debug("[|||||||||| ] URL for entry: {}".format(url + '?' + urllib.parse.urlencode(params)))
        response = requests.get(url, params=params)
        xml = response.content
        return xmltodict.parse(xml, process_namespaces=False, xml_attribs=False)

    @classmethod
    def get_coords_from_cadaster(cls, provincia, municipio, cadaster):
        params = {'Provincia': provincia, 'Municipio': municipio, 'SRS': 'EPSG:4230', 'RC': cadaster}
        url = cls.URL_LOCATIONS_BASE.format("/OVCCoordenadas.asmx/Consulta_CPMRC")

        logger.debug("[||||||||   ] URL for coords: {}".format(url + '?' + urllib.parse.urlencode(params)))

        response = requests.get(url, params=params)
        xml = response.content
        return xmltodict.parse(xml, process_namespaces=False, xml_attribs=False)