#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.parse
from urllib import error

from src.librecatastro.domain.cadaster_entry.cadaster_entry_xml import CadasterEntryXML
from src.librecatastro.scrapping.parser import Parser
from src.librecatastro.scrapping.scrapper import Scrapper
from src.librecatastro.scrapping.scrappers.scrapper_xml import ScrapperXML
from src.utils.catastro_logger import CadastroLogger

from dotmap import DotMap

from src.utils.elasticsearch_utils import ElasticSearchUtils
from src.utils.list_utils import ListUtils

'''Logger'''
logger = CadastroLogger(__name__).logger


class ParserXML(Parser):
    """Class that manages the processing of scrapped XML from Cadastro webservices"""

    def __init__(self):
        super().__init__()

    ''' Processing calls '''
    @classmethod
    def process_search_by_coordinates(cls, x, y, pictures=False):
        """
        Searches by coordinate from XML and processes the result.
        :param x: longitude
        :param y: latitude
        :param pictures: True if we want house plan pictures to be scrapped
        :return: List of CadasterEntry objects
        """

        results = []

        xml_dict_map = ScrapperXML.scrap_coord(x, y)
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

            entry = ScrapperXML.get_cadaster_entries_by_cadaster('', '', ''.join([pc1, pc2]))
            picture = None
            if entry.consulta_dnp.bico.bi.dt.loine != DotMap():
                prov_num = entry.consulta_dnp.bico.bi.dt.loine.cp
                city_num = entry.consulta_dnp.bico.bi.dt.cmc

                # Parcela
                if pictures and prov_num != DotMap() and city_num != DotMap():
                        picture = Scrapper.scrap_site_picture(prov_num, city_num, ''.join([pc1, pc2]))
                cadaster_entry = CadasterEntryXML(entry, x, y, picture)
                cadaster_entry.to_elasticsearch()
                results.append(cadaster_entry)
            elif entry.consulta_dnp.lrcdnp.rcdnp != DotMap():
                # Multiparcela
                parcelas = entry.consulta_dnp.lrcdnp.rcdnp
                if not isinstance(parcelas, list):
                    parcelas = [parcelas]

                for parcela in parcelas:

                    prov_num = parcela.dt.loine.cp
                    city_num = parcela.dt.cmc

                    cadaster = parcela.rc.pc1 if parcela.rc.pc1 != DotMap() else ''
                    cadaster += parcela.rc.pc2 if parcela.rc.pc2 != DotMap() else ''
                    cadaster += parcela.rc.car if parcela.rc.car != DotMap() else ''
                    cadaster += parcela.rc.cc1 if parcela.rc.cc1 != DotMap() else ''
                    cadaster += parcela.rc.cc2 if parcela.rc.cc2 != DotMap() else ''

                    if pictures and prov_num != DotMap() and city_num != DotMap():
                            picture = Scrapper.scrap_site_picture(prov_num, city_num, cadaster)

                    try:
                        # Try to get info by complete cadaster num
                        sub_entry = ScrapperXML.get_cadaster_entries_by_cadaster('', '', cadaster)
                    except:
                        # Cadastro did not return anything by cadaster entry (error? bug?)
                        # Try to get it by complete address
                        prov_name = parcela.dt.np
                        if prov_name is DotMap():
                            continue
                        city_name = parcela.dt.np
                        if city_name is DotMap():
                            continue
                        tv = parcela.ldt.locs.lous.lourb.dir.tv
                        if tv is DotMap():
                            tv = ''
                        nv = parcela.ldt.locs.lous.lourb.dir.nv
                        if nv is DotMap():
                            nv = ''
                        num = parcela.ldt.locs.lous.lourb.dir.pnp
                        if num is DotMap():
                            num = ''

                        loint = parcela.dt.locs.lous.lourb.loint
                        if loint is DotMap():
                            continue
                        bl = loint.bl
                        if bl == DotMap():
                            bl = ''
                        es = loint.es
                        if es == DotMap():
                            es = ''
                        pt = loint.pt
                        if es == DotMap():
                            pt = ''
                        pu = loint.pu
                        if es == DotMap():
                            pu = ''
                        sub_entry = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num, bl, es, pt, pu)

                    cadaster_entry = CadasterEntryXML(sub_entry, x, y, picture)
                    cadaster_entry.to_elasticsearch()

                    results.append(cadaster_entry)
        return results

    @classmethod
    def process_search_by_provinces(cls, prov_list, pictures=False, start_from='', matches=None):
        """
            Searches by province from XML and processes the result.
            :param prov_list: List of province names
            :param start_from: Name of the city of the first province to start from
            :param pictures: True if we want house plan pictures to be scrapped
            :param matches: Max number of matches (for debugging purporses mainly)
            :return: List of CadasterEntry objects
        """
        times = 0
        results = []

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
                    cadaster = ScrapperXML.get_cadaster_by_address(prov_name, city_name, tv, nv, counter)
                    res = cls.parse_xml_by_address(cadaster, prov_name, city_name, tv, nv, counter, pictures)
                    if len(res) < 1:
                        num_scrapping_fails -= 1
                    else:
                        num_scrapping_fails = 10
                        times += 1
                        results.append(res)
                        if matches is not None and times >= matches:
                            return ListUtils.flat(results)

                except urllib.error.HTTPError as e:
                    logger.error(
                        "ERROR AT ADDRESS {} {} {} {} {}".format(tv, nv, counter, prov_name, city_name))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("...sleeping due to connection reset...")
                    logger.debug("...sleeping due to connection reset...")
                    logger.error("=============================================")
                    ''' Could be a service Unavailable or denegation of service'''
                    num_scrapping_fails -= 1

                except Exception as e:
                    logger.error(
                        "ERROR AT ADDRESS {} {} {} {} {}".format(tv, nv, counter, prov_name, city_name))
                    logger.error("=============================================")
                    logger.error(e, exc_info=True)
                    logger.error("=============================================")
                    num_scrapping_fails -= 1

                counter += 1

        return results

    ''' Parsing calls '''

    @classmethod
    def parse_xml_by_address(cls, numerero_map, prov_name, city_name, tv, nv, num, pictures=False):
        """
        Parses an XML and crates a CadasterEntry object
        :param numerero_map: DotMap obtained from a previous call with information about the address to parse
        :param prov_name: Province Name
        :param city_name: City Name
        :param tv: Kind of way (Tipo de Via) - CL (calle), AV (Avenida) ...
        :param nv: Street name (Nombre de via)
        :param num: Street number (Numero de via)
        :param pictures: True if we want to scrap also house plan pictures. False otherwise.
        :return: List of CadasterEntry objects
        """
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

            coords_map = ScrapperXML.get_coords_from_cadaster(prov_name, city_name, cadaster_num)
            lon = coords_map.consulta_coordenadas.coordenadas.coord.geo.xcen
            if lon == DotMap():
                lon = None

            lat = coords_map.consulta_coordenadas.coordenadas.coord.geo.ycen
            if lat == DotMap():
                lat = None

            ''' Adding to tracking file'''
            logger.info('{},{}'.format(lon, lat))

            entry_map = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num)
            picture = None
            if entry_map.consulta_dnp.bico != DotMap():

                prov_num = entry_map.consulta_dnp.bico.bi.dt.loine.cp
                city_num = entry_map.consulta_dnp.bico.bi.dt.loine.cm

                if pictures and prov_num != DotMap() and city_num != DotMap():
                        picture = Scrapper.scrap_site_picture(prov_num, city_num, cadaster_num)

                # Parcela
                cadaster_entry = CadasterEntryXML(entry_map, lon, lat, picture)
                results.append(cadaster_entry)
                cadaster_entry.to_elasticsearch()

            elif entry_map.consulta_dnp.lrcdnp.rcdnp != DotMap():
                # Multiparcela
                for site in entry_map.consulta_dnp.lrcdnp.rcdnp:
                    site_map = DotMap(site)

                    if site_map.rc == DotMap():
                        continue

                    # Multiparcela
                    parcelas = entry_map.consulta_dnp.lrcdnp.rcdnp
                    if not isinstance(parcelas, list):
                        parcelas = [parcelas]
                    for parcela in parcelas:
                        cadaster = parcela.rc.pc1 if parcela.rc.pc1 != DotMap() else ''
                        cadaster += parcela.rc.pc2 if parcela.rc.pc2 != DotMap() else ''
                        cadaster += parcela.rc.car if parcela.rc.car != DotMap() else ''
                        cadaster += parcela.rc.cc1 if parcela.rc.cc1 != DotMap() else ''
                        cadaster += parcela.rc.cc2 if parcela.rc.cc2 != DotMap() else ''

                        prov_num = parcela.dt.loine.cp
                        city_num = parcela.dt.cmc

                        if pictures and prov_num != DotMap() and city_num != DotMap():
                                picture = Scrapper.scrap_site_picture(prov_num, city_num, cadaster)

                        try:
                            # Try to get info by complete cadaster num
                            sub_entry = ScrapperXML.get_cadaster_entries_by_cadaster(prov_name, city_name, cadaster)
                        except:
                            # Cadastro did not return anything by cadaster entry (error? bug?)
                            # Try to get it by complete address
                            loint = parcela.dt.locs.lous.lourb.loint
                            if loint is DotMap():
                                continue
                            bl = loint.bl
                            if bl == DotMap():
                                bl = ''
                            es = loint.es
                            if es == DotMap():
                                es = ''
                            pt = loint.pt
                            if es == DotMap():
                                pt = ''
                            pu = loint.pu
                            if es == DotMap():
                                pu = ''
                            sub_entry = ScrapperXML.get_cadaster_entries_by_address(prov_name, city_name, tv, nv, num, bl, es, pt, pu)

                        cadaster_entry = CadasterEntryXML(sub_entry, lon, lat, picture)
                        cadaster_entry.to_elasticsearch()

                        results.append(cadaster_entry)

        return results
