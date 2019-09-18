import urllib.parse
from urllib import error

from time import sleep

import requests
import xmltodict as xmltodict

from src.librecatastro.domain.cadaster_entry.cadaster_entry_xml import CadasterEntryXML
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class ScrapperXML:
    """Scrapper class for Catastro HTML"""

    '''Catastro web services parametrized'''
    URL_LOCATIONS_BASE = "http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC{}"

    def __init__(self):
        pass

    """ Scrapping main calls """

    @classmethod
    def scrap_all_addresses(cls, prov_list):
        """Scraps properties by addresses. ONLY URBAN"""

        provinces = ScrapperXML.get_provinces()['consulta_provinciero']['provinciero']['prov']

        for province in provinces:
            prov_name = province['np']

            if len(prov_list) > 0 and prov_name not in prov_list:
                continue

            cities = ScrapperXML.get_cities(prov_name)['consulta_municipiero']['municipiero']['muni']
            for city in cities:
                city_name = city['nm']
                addresses = ScrapperXML.get_addresses(prov_name, city_name)['consulta_callejero']['callejero'][
                    'calle']
                for address in addresses:
                    address_dir = address['dir']
                    tv = address_dir['tv']
                    nv = address_dir['nv']

                    num_scrapping_fails = 10
                    counter = 1
                    while num_scrapping_fails > 0:
                        try:
                            cadaster = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, counter)
                            if 'lerr' in cadaster['consulta_numerero'] and \
                                    'err' in cadaster['consulta_numerero']['lerr'] and \
                                    'cod' in cadaster['consulta_numerero']['lerr']['err'] and \
                                    cadaster['consulta_numerero']['lerr']['err']['cod'] == '43':
                                num_scrapping_fails -= 1
                            else:
                                logger.debug("|||||       ] FOUND!")

                                numps = cadaster['consulta_numerero']['numerero']['nump']

                                if not isinstance(numps, list):
                                    numps = [numps]

                                for nump in numps:
                                    num = nump['num']['pnp']
                                    cadaster_num = nump['pc']['pc1'] + nump['pc']['pc2']

                                    coords = ScrapperXML.get_coords_from_cadaster(prov_name, city_name,
                                                                                  cadaster_num)
                                    lon = coords['consulta_coordenadas']['coordenadas']['coord']['geo']['xcen']
                                    lat = coords['consulta_coordenadas']['coordenadas']['coord']['geo']['ycen']

                                    ''' Adding to tracking file'''
                                    logger.info('{},{}'.format(lon, lat))

                                    num_scrapping_fails = 10

                                    entry = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv,
                                                                                        nv, num)

                                    if 'bico' in entry['consulta_dnp']:
                                        # Parcela
                                        cadaster_entry = CadasterEntryXML(entry, lon, lat)
                                        cadaster_entry.to_elasticsearch()
                                    elif 'lrcdnp' in entry['consulta_dnp']:
                                        # Multiparcela
                                        for site in entry['consulta_dnp']['lrcdnp']['rcdnp']:
                                            cadaster = site['rc']['pc1'] + \
                                                       site['rc']['pc2'] + \
                                                       site['rc']['car'] + \
                                                       site['rc']['cc1'] + \
                                                       site['rc']['cc2']
                                            sub_entry = ScrapperXML.get_cadaster_entries_by_cadaster(prov_name,
                                                                                                     city_name,
                                                                                                     cadaster)
                                            cadaster_entry = CadasterEntryXML(sub_entry, lon, lat)
                                            cadaster_entry.to_elasticsearch()
                                            sleep(config['sleep_time'])

                                    logger.debug("[|||||||||||] SUCCESS!")
                                    sleep(config['sleep_time'])

                        except urllib.error.HTTPError as e:
                            logger.error(
                                "ERROR AT ADDRESS {} {} {} {} {}".format(tv, nv, num, prov_name, city_name))
                            logger.error("=============================================")
                            logger.error(e, exc_info=True)
                            logger.error("...sleeping...")
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
                        sleep(config['sleep_time'])



    """ Scrapping secondary calls """


    @classmethod
    def get_coords_from_cadaster(cls, provincia, municipio, cadaster):
        params = {'Provincia': provincia, 'Municipio': municipio, 'SRS': 'EPSG:4230', 'RC': cadaster}
        url = cls.URL_LOCATIONS_BASE.format("/OVCCoordenadas.asmx/Consulta_CPMRC")

        logger.debug("[||||||||   ] URL for coords: {}".format(url + '?' + urllib.parse.urlencode(params)))

        response = requests.get(url, params=params)
        xml = response.content
        return xmltodict.parse(xml, process_namespaces=False, xml_attribs=False)


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
                                        planta=None,
                                        puerta=None):
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
        params = {"Provincia": provincia,
                  "Municipio": municipio,
                  "RC": rc}

        url = cls.URL_LOCATIONS_BASE.format("/OVCCallejero.asmx/Consulta_DNPRC")
        logger.debug("[|||||||||| ] URL for entry: {}".format(url + '?' + urllib.parse.urlencode(params)))
        response = requests.get(url, params=params)
        xml = response.content
        return xmltodict.parse(xml, process_namespaces=False, xml_attribs=False)


    @classmethod
    def Consulta_DNPPP(cls, provincia, municipio, poligono, parcela):
        """Proporciona los datos catastrales no protegidos de un inmueble
           Este servicio es idéntico al de "Consulta de DATOS CATASTRALES NO
           PROTEGIDOS de un inmueble identificado por su localización" en todo
           excepto en los parámetros de entrada.
           :param str: Nombre de la provincia
           :param str: Nombre del municipio
           :param str: Codigo del poligono
           :param str: Codigo de la parcela
           :return: Retorna un dicionario con los datos de la consutla
           :rtype: dict
        """

        params = {'Provincia': provincia,
                  'Municipio': municipio,
                  'Poligono': poligono,
                  'Parcela': parcela}

        url = cls.URL_LOCATIONS_BASE + "/OVCCallejero.asmx/Consulta_DNPPP"
        response = requests.get(url, params=params)
        return xmltodict.parse(response.content, process_namespaces=False, xml_attribs=False)


    @classmethod
    def Consulta_DNPLOC_Codigos(cls, provincia, municipio, sigla, nombrevia, numero, bloque=None, escalera=None,
                                planta=None, puerta=None):
        """Proporciona la lista de todos los inmuebles que coinciden.
           Este servicio puede devolver o bien la lista de todos los inmuebles que
           coinciden con los criterios de búsqueda, proporcionando para cada
           inmueble la referencia catastral y su localización
           (bloque/escalera/planta/puerta) o bien,en el caso de que solo exista un
           inmueble con los parámetros de entrada indicados, proporciona los datos
           de un inmueble.
           :param str: Nombre de la provincia
           :param str: Nombre del municipio
           :param str: Sigla
           :param str: Nombre de la via
           :param str,int: Numero de inmueble
           :param str,int: Numero de bloque
           :param str: Escalera
           :param str,int: Numero de planta
           :param str,int: Numero de puerta
           :return: Retorna un dicionario con los datos de la consutla
           :rtype: dict
        """

        params = {
            'Provincia': provincia,
            'Municipio': municipio,
            'Sigla': sigla,
            'Calle': nombrevia,
            'Numero': str(numero)}
        if bloque:
            params['Bloque'] = bloque
        else:
            params['Bloque'] = ''
        if planta:
            params['Escalera'] = escalera
        else:
            params['Escalera'] = ''
        if puerta:
            params['Puerta'] = str(puerta)
        else:
            params['Puerta'] = ''
        if escalera:
            params['Escalera'] = str(escalera)
        else:
            params['Escalera'] = ''

        url = cls.URL_LOCATIONS_BASE + "/OVCCallejero.asmx/Consulta_DNPLOC"
        response = requests.get(url, params=params)
        return xmltodict.parse(response.content, process_namespaces=False, xml_attribs=False)


    @classmethod
    def Consulta_DNPRC_Codigos(cls, provincia, municipio, rc):
        """Proporciona los datos catastrales de un inmueble,
           Este servicio es idéntico al de "Consulta de DATOS CATASTRALES NO
           PROTEGIDOS de un inmueble identificado por su localización"
           en todo excepto en los parámetros de entrada.
           :param str: Nombre de la provincia
           :param str: Nombre del municipio
           :param str: Referencia catastral
           :return: Retorna un dicionario con los datos de la consutla
           :rtype: dict
        """

        params = {
            'Provincia': provincia,
            'Municipio': municipio,
            'RC': rc}

        url = cls.URL_LOCATIONS_BASE + "/OVCCallejero.asmx/Consulta_DNPRC"
        response = requests.get(url, params=params)
        return xmltodict.parse(response.content, process_namespaces=False, xml_attribs=False)


    @classmethod
    def Consulta_DNPPP_Codigos(cls, provincia, municipio, poligono, parcela):
        """Proporciona los datos catastrales de un inmueble.
           Este servicio es idéntico al de "Consulta de DATOS CATASTRALES NO
           PROTEGIDOS de un inmueble identificado por su localización" en todo
           excepto en los parámetros de entrada.
           :param str: Nombre de la provincia
           :param str: Nombre del municipio
           :param str: Codigo del poligono
           :param str: Codigo de la parcela
           :return: Retorna un dicionario con los datos de la consutla
           :rtype: dict
        """

        params = {
            "Provincia": provincia,
            "Municipio": municipio,
            "Poligono": poligono,
            "Parcela": parcela}

        url = cls.URL_LOCATIONS_BASE + "/OVCCallejero.asmx/Consulta_DNPPP"
        response = requests.get(url, params=params)
        return xmltodict.parse(response.content, process_namespaces=False, xml_attribs=False)
