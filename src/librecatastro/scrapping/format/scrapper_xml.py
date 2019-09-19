import json
import urllib.parse
from urllib import error

from time import sleep

import requests
import xmltodict

from src.librecatastro.domain.cadaster_entry.cadaster_entry_xml import CadasterEntryXML
from src.librecatastro.scrapping.scrapper import Scrapper
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class ScrapperXML(Scrapper):
    """Scrapper class for Catastro XML"""

    def __init__(self):
        pass

    """ Scrapping main calls """

    @classmethod
    def scrap_coord(cls, x, y, pictures=False):
        """Scraps properties by coordinates"""
        params = {'SRS': 'EPSG:4230', 'Coordenada_X': x, 'Coordenada_Y': y}
        url = cls.URL_LOCATIONS_BASE.format("/OVCCoordenadas.asmx/Consulta_RCCOOR")
        response = requests.get(url, params=params)

        logger.debug("====Longitude: {} Latitude: {}====".format(x, y))
        logger.debug("[|||        ] URL for coordinates: {}".format(url + '?' + urllib.parse.urlencode(params)))

        xml = response.content
        xml_dict = xmltodict.parse(xml, process_namespaces=False, xml_attribs=False)
        pc1 = None
        pc2 = None
        if 'coordenadas' in xml_dict['consulta_coordenadas'] and 'coord' in xml_dict['consulta_coordenadas']['coordenadas']:
            pc1 = xml_dict['consulta_coordenadas']['coordenadas']['coord']['pc']['pc1'] if 'pc' in xml_dict['consulta_coordenadas']['coordenadas']['coord'] else None
            pc2 = xml_dict['consulta_coordenadas']['coordenadas']['coord']['pc']['pc2'] if 'pc' in xml_dict['consulta_coordenadas']['coordenadas']['coord'] else None
        if pc1 is not None and pc2 is not None:
            logger.debug("|||||       ] FOUND!")

            entry = cls.get_cadaster_entries_by_cadaster('', '', ''.join([pc1,pc2]))
            cadaster_entry = CadasterEntryXML(entry, x, y)
            cadaster_entry.to_elasticsearch()
            logger.debug("[|||||||||||] SUCCESS!")
            sleep(config['sleep_time'])

    @classmethod
    def scrap_provinces(cls, prov_list, pictures=False):
        """Scraps properties by addresses"""

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
                            cadaster = cls.get_cadaster_by_address(prov_name, city_name, tv, nv, counter)
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

                                    coords = cls.get_coords_from_cadaster(prov_name, city_name,
                                                                                  cadaster_num)
                                    lon = coords['consulta_coordenadas']['coordenadas']['coord']['geo']['xcen']
                                    lat = coords['consulta_coordenadas']['coordenadas']['coord']['geo']['ycen']

                                    ''' Adding to tracking file'''
                                    logger.info('{},{}'.format(lon, lat))

                                    num_scrapping_fails = 10

                                    entry = cls.get_cadaster_entries_by_address(prov_name, city_name, tv,
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
                                            sub_entry = cls.get_cadaster_entries_by_cadaster(prov_name,
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
