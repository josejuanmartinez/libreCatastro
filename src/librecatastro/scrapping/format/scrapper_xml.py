import urllib.parse
from urllib import error

from time import sleep

import requests
import xmltodict

from src.librecatastro.domain.cadaster_entry.cadaster_entry_xml import CadasterEntryXML
from src.librecatastro.scrapping.scrapper import Scrapper
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

from dotmap import DotMap

'''Logger'''
logger = CadastroLogger(__name__).logger


class ScrapperXML(Scrapper):
    """Scrapper class for Catastro XML"""

    def __init__(self):
        super().__init__()

    """ Scrapping main calls """

    @classmethod
    def scrap_coord(cls, x, y, pictures=False):
        """Scraps properties by coordinates"""

        results = []

        params = {'SRS': 'EPSG:4230', 'Coordenada_X': x, 'Coordenada_Y': y}
        url = cls.URL_LOCATIONS_BASE.format("/OVCCoordenadas.asmx/Consulta_RCCOOR")
        response = requests.get(url, params=params)

        logger.debug("====Longitude: {} Latitude: {}====".format(x, y))
        logger.debug("URL for coordinates: {}".format(url + '?' + urllib.parse.urlencode(params)))

        xml_dict_map = DotMap(xmltodict.parse(response.content, process_namespaces=False, xml_attribs=False))
        pc1 = None
        pc2 = None
        if xml_dict_map.consulta_coordenadas.coordenadas.coord.pc != DotMap():
            pc1 = xml_dict_map.consulta_coordenadas.coordenadas.coord.pc.pc1
            if pc1 == DotMap():
                pc1 = None

            pc2 = xml_dict_map.consulta_coordenadas.coordenadas.coord.pc.pc2
            if pc2 == DotMap():
                pc2 = None

        if pc1 is not None and pc2 is not None:

            entry = cls.get_cadaster_entries_by_cadaster('', '', ''.join([pc1, pc2]))
            picture = None
            if entry.consulta_dnp.bico.bi.dt.loine != DotMap():
                # Parcela
                if pictures:
                    prov_num = entry.consulta_dnp.bico.bi.dt.loine.cp
                    city_num = entry.consulta_dnp.bico.bi.dt.cmc
                    if prov_num != DotMap() and city_num != DotMap():
                        picture = cls.scrap_site_picture(prov_num, city_num, ''.join([pc1, pc2]))
                cadaster_entry = CadasterEntryXML.create_from_bico(entry, x, y, picture)
                cadaster_entry.to_elasticsearch()
                sleep(config['sleep_time'])
                results.append(cadaster_entry)
            elif entry.consulta_dnp.lrcdnp.rcdnp != DotMap():
                # Multiparcela
                parcelas = entry.consulta_dnp.lrcdnp.rcdnp
                if not isinstance(parcelas, list):
                    parcelas = [parcelas]
                for parcela in parcelas:
                    if pictures:
                        prov_num = parcela.dt.loine.cp
                        city_num = parcela.dt.cmc
                        if prov_num != DotMap() and city_num != DotMap():
                            picture = cls.scrap_site_picture(prov_num, city_num, ''.join([pc1, pc2]))

                    cadaster = parcela.rc.pc1 if parcela.rc.pc1 != DotMap() else ''
                    cadaster += parcela.rc.pc2 if parcela.rc.pc2 != DotMap() else ''
                    cadaster += parcela.rc.car if parcela.rc.car != DotMap() else ''
                    cadaster += parcela.rc.cc1 if parcela.rc.cc1 != DotMap() else ''
                    cadaster += parcela.rc.cc2 if parcela.rc.cc2 != DotMap() else ''

                    parcela = cls.get_cadaster_entries_by_cadaster('', '', cadaster)
                    cadaster_entry = CadasterEntryXML(parcela, x, y, picture)
                    cadaster_entry.to_elasticsearch()

                    results.append(cadaster_entry)

                    sleep(config['sleep_time'])
        return results

    @classmethod
    def scrap_provinces(cls, prov_list, pictures=False, start_from=''):
        for prov_name, prov_num, city_name, city_num, address, tv, nv in cls.get_address_iter(prov_list, start_from):
            if tv == DotMap() or nv == DotMap():
                continue

            num_scrapping_fails = 10
            counter = 1
            while num_scrapping_fails > 0:
                try:
                    cadaster = cls.get_cadaster_by_address(prov_name, city_name, tv, nv, counter)
                    res = cls.process_xml_by_address(cadaster, prov_name, city_name, tv, nv, pictures)
                    if len(res) < 1:
                        num_scrapping_fails -= 1
                    else:
                        num_scrapping_fails = 10
                    sleep(config['sleep_time'])

                except urllib.error.HTTPError as e:
                    logger.error(
                        "ERROR AT ADDRESS {} {} {} {} {}".format(tv, nv, counter, prov_name, city_name))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("...sleeping...")
                    logger.error("=============================================")
                    ''' Could be a service Unavailable or denegation of service'''
                    num_scrapping_fails -= 1
                    sleep(config['sleep_dos_time'])

                except Exception as e:
                    logger.error(
                        "ERROR AT ADDRESS {} {} {} {} {}".format(tv, nv, counter, prov_name, city_name))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("=============================================")
                    num_scrapping_fails -= 1

                counter += 1
                sleep(config['sleep_time'])

    @classmethod
    def process_xml_by_address(cls, numerero_map, prov_name, city_name, tv, nv, pictures=False):
        results = []
        if numerero_map.consulta_numerero.lerr.err.cod != DotMap():
            return results

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

            coords_map = cls.get_coords_from_cadaster(prov_name, city_name, cadaster_num)

            lon = coords_map.consulta_coordenadas.coordenadas.coord.geo.xcen
            if lon == DotMap():
                lon = None

            lat = coords_map.consulta_coordenadas.coordenadas.coord.geo.ycen
            if lat == DotMap():
                lat = None

            ''' Adding to tracking file'''
            logger.info('{},{}'.format(lon, lat))

            entry_map = cls.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num)
            picture = None
            if entry_map.consulta_dnp.bico != DotMap():

                prov_num = entry_map.consulta_dnp.bico.bi.dt.loine.cp
                city_num = entry_map.consulta_dnp.bico.bi.dt.loine.cm

                if pictures and prov_num != DotMap() and city_num != DotMap():
                        picture = cls.scrap_site_picture(prov_num, city_num, cadaster_num)

                # Parcela
                cadaster_entry = CadasterEntryXML(entry_map, lon, lat, picture)
                results.append(cadaster_entry)
                cadaster_entry.to_elasticsearch()

                sleep(config['sleep_time'])
            elif entry_map.consulta_dnp.lrcdnp.rcdnp != DotMap():
                # Multiparcela
                for site in entry_map.consulta_dnp.lrcdnp.rcdnp:
                    site_map = DotMap(site)

                    if site_map.rc == DotMap():
                        continue

                    cadaster = site_map.rc.pc1 + site_map.rc.pc2 + site_map.rc.car + site_map.rc.cc1 + site_map.rc.cc2
                    sub_entry = cls.get_cadaster_entries_by_cadaster(prov_name, city_name, cadaster)

                    prov_num = entry_map.consulta_dnp.lrcdnp.rcdnp.loine.cp
                    city_num = entry_map.consulta_dnp.lrcdnp.rcdnp.loine.cm

                    if pictures and prov_num != DotMap() and city_num != DotMap():
                        picture = cls.scrap_site_picture(prov_num, city_num, cadaster)

                    cadaster_entry = CadasterEntryXML(sub_entry, lon, lat, picture)
                    results.append(cadaster_entry)
                    cadaster_entry.to_elasticsearch()
                    sleep(config['sleep_time'])

        return results
