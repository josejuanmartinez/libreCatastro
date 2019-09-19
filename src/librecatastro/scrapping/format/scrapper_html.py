import re
import urllib.error
from time import sleep

from urllib.request import urlopen
from xml.etree import ElementTree
from bs4 import BeautifulSoup

from src.librecatastro.domain.cadaster_entry.cadaster_entry_html import CadasterEntryHTML
from src.librecatastro.scrapping.scrapper import Scrapper
from src.settings import config

from src.utils.cadastro_logger import CadastroLogger


'''Logger'''
logger = CadastroLogger(__name__).logger


class ScrapperHTML(Scrapper):
    """Scrapper class for Catastro HTML"""

    def __init__(self):
        super().__init__()

    '''Catastro web services parametrized'''
    URL = "http://ovc.catastro.meh.es/ovcservweb/ovcswlocalizacionrc/ovccoordenadas.asmx/Consulta_RCCOOR?SRS=EPSG:4230&Coordenada_X={}&Coordenada_Y={}"
    URL_REF = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCListaBienes.aspx?rc1={}&rc2={}"
    URL_REF_FULL = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?RefC={}&RCCompleta={}&del={}&mun={}"

    '''Information to scrap from HTML'''
    description_field_names = [u'Referencia catastral', u'Localización', u'Clase', u'Uso principal', u'Superficie construida', u'Año construcción']
    gsurface_field_names = [u'Superficie gráfica']

    """ Coordinates scrapping calls """

    @classmethod
    def scrap_coord(cls, x, y):
        logger.debug("====Longitude: {} Latitude: {}====".format(x, y))
        url = cls.URL.format(x, y)
        logger.debug("[|||        ] URL for coordinates: {}".format(url))
        f = urlopen(url)
        data = f.read()
        root = ElementTree.fromstring(data)
        pc1 = root.find(
            "{http://www.catastro.meh.es/}coordenadas//{http://www.catastro.meh.es/}coord//{http://www.catastro.meh.es/}pc//{http://www.catastro.meh.es/}pc1")
        pc2 = root.find(
            "{http://www.catastro.meh.es/}coordenadas//{http://www.catastro.meh.es/}coord//{http://www.catastro.meh.es/}pc//{http://www.catastro.meh.es/}pc2")
        if pc1 is None or pc2 is None:
            return []
        else:
            logger.debug("|||||       ] FOUND!")
            cadaster = ''.join([pc1.text, pc2.text])
            cadaster_entries = cls.scrap_cadaster(cadaster, x, y)
            for cadaster_entry in cadaster_entries:
                cadaster_entry.to_elasticsearch()


    @classmethod
    def scrap_provinces(cls, prov_list):
        """Scraps properties by addresses"""

        provinces = cls.get_provinces()['consulta_provinciero']['provinciero']['prov']

        for province in provinces:
            prov_name = province['np']

            if len(prov_list) > 0 and prov_name not in prov_list:
                continue

            cities = cls.get_cities(prov_name)['consulta_municipiero']['municipiero']['muni']
            for city in cities:
                city_name = city['nm']
                addresses = (cls.get_addresses(prov_name, city_name)['consulta_callejero']['callejero'][
                    'calle'])

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

                                    coords = cls.get_coords_from_cadaster(prov_name, city_name,cadaster_num)
                                    lon = coords['consulta_coordenadas']['coordenadas']['coord']['geo']['xcen']
                                    lat = coords['consulta_coordenadas']['coordenadas']['coord']['geo']['ycen']

                                    ''' Adding to tracking file'''
                                    logger.info('{},{}'.format(lon, lat))

                                    num_scrapping_fails = 10

                                    cadaster_list = cls.scrap_cadaster(cadaster_num, lon, lat)

                                    for cadaster in cadaster_list:
                                        cadaster.to_elasticsearch()

                                counter += 1
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


    """ Parsing """

    @classmethod
    def parse_html_parcela(cls, parsed_html, x=None, y=None):
        description = parsed_html.find(id='ctl00_Contenido_tblInmueble')

        descriptive_data = dict()
        descriptive_data[u'Longitud'] = x
        descriptive_data[u'Latitud'] = y
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
                        descriptive_data[field_name] = field_value.encode_contents().decode('utf-8').replace('<br/>', config['separator']).replace('<br>', config['separator'])

        '''Graphical Surface'''
        fields = parsed_html.find(id='ctl00_Contenido_tblFinca').find_all('div')
        for field in fields:
            field_header = field.find('span')
            for field_name in cls.gsurface_field_names:
                if field_name in field_header.text:
                    field_value = field.find('label', {"class": "control-label black text-left"})
                    descriptive_data[field_name] = field_value.text.strip()

        '''Constructions'''
        constructions_table = parsed_html.find(id='ctl00_Contenido_tblLocales');
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

            descriptive_data[u'Construcciones'].append(dict(uso=columns[0].text, escalera=columns[1].text, planta=columns[2].text, puerta=columns[3].text, superficie=columns[4].text, tipo=columns[5].text, fecha=columns[6].text))

        cadaster_entry = CadasterEntryHTML(descriptive_data)
        return cadaster_entry

    @classmethod
    def scrap_cadaster_full_code(cls, full_cadaster, delimitacion, municipio, x=None, y=None):
        url_ref = cls.URL_REF_FULL.format(full_cadaster, full_cadaster, delimitacion, municipio)
        logger.debug("-->FULL URL for cadastral data: {}".format(url_ref))
        f_ref = urlopen(url_ref)
        data_ref = f_ref.read()
        html = str(data_ref.decode('utf-8'))
        parsed_html = BeautifulSoup(html, features="html.parser")
        return ScrapperHTML.parse_html_parcela(parsed_html, x, y)

    @classmethod
    def scrap_cadaster(cls, cadaster, x=None, y=None):
        rc_1 = cadaster[0:7]
        rc_2 = cadaster[7:14]
        url_ref = cls.URL_REF.format(rc_1, rc_2)

        logger.debug("[||||||||   ] URL for cadastral data: {}".format(url_ref))

        f_ref = urlopen(url_ref)
        data_ref = f_ref.read()
        html = str(data_ref.decode('utf-8'))
        parsed_html = BeautifulSoup(html, features="html.parser")

        delimitacion = ''
        delimitacion_search = re.search(r'del=([0-9]+)&', html)
        if delimitacion_search:
            delimitacion = delimitacion_search.group(1)

        municipio = ''
        municipio_search = re.search(r'mun=([0-9]+)&', html)
        if municipio_search:
            municipio = municipio_search.group(1)

        description = parsed_html.find(id='ctl00_Contenido_tblInmueble')

        cadasters = []
        if description is None:
            logger.debug("Multiparcela found!")
            ''' Multiparcela with multiple cadasters '''

            all_cadasters = parsed_html.findAll("div", {"id": re.compile('heading[0-9]+')})
            logger.debug("->Parcelas found: {}".format(len(all_cadasters)))
            for partial_cadaster in all_cadasters:
                partial_cadaster_ref = partial_cadaster.find("b")
                logger.debug("-->Partial cadaster: {}".format(partial_cadaster_ref.text))
                partial_cadaster_text = partial_cadaster_ref.text.strip()
                cadaster = ScrapperHTML.scrap_cadaster_full_code(partial_cadaster_text, delimitacion, municipio, x, y)

                sleep(config['sleep_time'])

                cadasters.append(cadaster)
        else:
            cadaster = ScrapperHTML.parse_html_parcela(parsed_html, x, y)
            cadasters.append(cadaster)

        logger.debug("[|||||||||||] SUCCESS!")
        sleep(config['sleep_time'])
        return cadasters
