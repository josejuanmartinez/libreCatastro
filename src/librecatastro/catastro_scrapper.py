import random
import re
import time

from time import sleep
from urllib.request import urlopen
from xml.etree import ElementTree
from bs4 import BeautifulSoup

from src.librecatastro.domain.cadaster_entry import CadasterEntry
from src.settings import config

from src.utils.cadastro_logger import CadastroLogger
from src.utils.list_utils import ListUtils

"""Constants"""

'''Spain geocoordinates'''
LONGITUDE = (4289603, -18024300)  # *1000000
LATITUDE = (43769200, 27725500)   # *1000000

'''Scale for scrapping'''
SCALE = 1000000
TRUNCATE_RIGHT = 4

'''Enumerator for tuple access'''
MAX = 0
MIN = 1

'''Catastro web services parametrized'''
URL = "http://ovc.catastro.meh.es/ovcservweb/ovcswlocalizacionrc/ovccoordenadas.asmx/Consulta_RCCOOR?SRS=EPSG:4230&Coordenada_X={}&Coordenada_Y={}"
URL_REF = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCListaBienes.aspx?rc1={}&rc2={}"
URL_REF_FULL = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?RefC={}&RCCompleta={}&del={}&mun={}"

'''Information to scrap from HTML'''
field_names = (u'Referencia catastral', u'Localización', u'Clase', u'Uso principal', u'Superficie construida', u'Año construcción')

'''Logger'''
logger = CadastroLogger(__name__).logger


class CadastroScrapper:
    """Scrapper class for Catastro HTML"""

    def __init__(self):
        pass

    """ Scrapping main calls """
    @staticmethod
    def scrap_all():
        results = []
        for j in range(LONGITUDE[MIN], LONGITUDE[MAX]):
            for i in range(LATITUDE[MIN], LATITUDE[MAX]):
                result = CadastroScrapper.scrap_coord(i, j)
                if result is not None:
                    results.append(result)
        return ListUtils.flat(results)

    @staticmethod
    def scrap_results_by_time(seconds):
        start_time = time.time()
        results = []

        finished = False
        for j in range(LONGITUDE[MIN], LONGITUDE[MAX]):
            for i in range(LATITUDE[MIN], LATITUDE[MAX]):
                if finished:
                    break
                result = CadastroScrapper.scrap_coord(i, j)
                if result is not None:
                    results.append(result)
                    now = time.time()
                    elapsed_time = now - start_time
                    if elapsed_time > seconds:
                        finished = True
                        break
                sleep(5)
            if finished:
                break
        return ListUtils.flat(results)

    @staticmethod
    def scrap_results_linear_x_times(times):
        results = []
        counter = times

        finished = False
        for x in range(LONGITUDE[MIN], LONGITUDE[MAX]):
            for y in range(LATITUDE[MIN], LATITUDE[MAX]):

                x_scaled = x / SCALE
                x_scaled = str(x_scaled)[:-TRUNCATE_RIGHT]
                y_scaled = y / SCALE
                y_scaled = str(y_scaled)[:-TRUNCATE_RIGHT]
                result = CadastroScrapper.scrap_coord(x_scaled, y_scaled)
                if result is not None:
                    results.append(result)
                    counter -= 1
                    if counter == 0:
                        finished = True
                        break
                sleep(5)

            if finished:
                break

        return ListUtils.flat(results)

    @staticmethod
    def scrap_results_random_x_times(times):
        results = []
        counter = times
        while counter > 0:
            x = random.randrange(LONGITUDE[MIN], LONGITUDE[MAX])
            y = random.randrange(LATITUDE[MIN], LATITUDE[MAX])

            x_scaled = x / SCALE
            x_scaled = str(x_scaled)[:-TRUNCATE_RIGHT]
            y_scaled = y / SCALE
            y_scaled = str(y_scaled)[:-TRUNCATE_RIGHT]
            cadaster_entry = CadastroScrapper.scrap_coord(x_scaled, y_scaled)

            if cadaster_entry is not None:
                results.append(cadaster_entry)
                counter -= 1
                if counter == 0:
                    break
            sleep(5)

        #ontology_converter = OntologyConverter()
        #print(ontology_converter.cadastro_dict_to_ontology(results))
        logger.info("====PROCESSING FINISHED====")
        logger.info("Results found: {}".format(times))
        logger.info(results)
        return ListUtils.flat(results)

    """ Scrapping secondary calls """
    @staticmethod
    def parse_html_parcela(parsed_html, x=None, y=None):
        description = parsed_html.find(id='ctl00_Contenido_tblInmueble')
        descriptive_data = dict()
        descriptive_data[u'Longitud'] = x
        descriptive_data[u'Latitud'] = y
        ''' Parcela '''
        fields = description.find_all('div')
        for field in fields:
            field_header = field.find('span')
            for field_name in field_names:
                if field_name in field_header.text:
                    field_value = field.find('label', {"class": "control-label black text-left"})
                    descriptive_data[field_name] = field_value.text.strip()

                    if field_header.text == u'Referencia catastral':
                        descriptive_data[field_name] = descriptive_data[field_name].split(' ')[0]
                        descriptive_data[field_name] = descriptive_data[field_name].split('\xa0')[0]
                    elif field_header.text == u'Localización':
                        descriptive_data[field_name] = field_value.encode_contents().decode('utf-8').replace('<br/>',config['separator']).replace('<br>', config['separator'])

        cadaster_entry = CadasterEntry(descriptive_data)
        logger.info(cadaster_entry.to_json())
        return cadaster_entry

    @staticmethod
    def scrap_cadaster_full_code(full_cadaster, delimitacion, municipio, x=None, y=None):
        url_ref = URL_REF_FULL.format(full_cadaster, full_cadaster, delimitacion, municipio)
        logger.info("-->FULL URL for cadastral data: {}".format(url_ref))
        f_ref = urlopen(url_ref)
        data_ref = f_ref.read()
        html = str(data_ref.decode('utf-8'))
        parsed_html = BeautifulSoup(html, features="html.parser")
        return CadastroScrapper.parse_html_parcela(parsed_html, x, y)

    @staticmethod
    def scrap_cadaster(cadaster, x=None, y=None):
        rc_1 = cadaster[0:7]
        rc_2 = cadaster[7:14]
        url_ref = URL_REF.format(rc_1, rc_2)
        logger.info("-->URL for cadastral data: {}".format(url_ref))
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
            logger.info("Multiparcela found!")
            ''' Multiparcela with multiple cadasters '''

            all_cadasters = parsed_html.findAll("div", {"id": re.compile('heading[0-9]+')})
            logger.info("->Parcelas found: {}".format(len(all_cadasters)))
            for partial_cadaster in all_cadasters:
                partial_cadaster_ref = partial_cadaster.find("b")
                logger.info("-->Partial cadaster: {}".format(partial_cadaster_ref.text))
                partial_cadaster_text = partial_cadaster_ref.text.strip()
                cadaster = CadastroScrapper.scrap_cadaster_full_code(partial_cadaster_text, delimitacion, municipio, x, y)
                cadasters.append(cadaster)
        else:
            cadaster = CadastroScrapper.parse_html_parcela(parsed_html, x, y)
            cadasters.append(cadaster)

        return cadasters

    @staticmethod
    def scrap_coord(x, y):
        logger.info("====Longitude: {} Latitude: {}====".format(x, y))
        url = URL.format(x, y)
        logger.info("-->URL for coordinates: {}".format(url))
        f = urlopen(url)
        data = f.read()
        root = ElementTree.fromstring(data)
        pc1 = root.find("{http://www.catastro.meh.es/}coordenadas//{http://www.catastro.meh.es/}coord//{http://www.catastro.meh.es/}pc//{http://www.catastro.meh.es/}pc1")
        pc2 = root.find("{http://www.catastro.meh.es/}coordenadas//{http://www.catastro.meh.es/}coord//{http://www.catastro.meh.es/}pc//{http://www.catastro.meh.es/}pc2")
        if pc1 is None or pc2 is None:
            return None
        else:
            logger.info("-->FOUND!")
        cadaster = ''.join([pc1.text,pc2.text])

        return CadastroScrapper.scrap_cadaster(cadaster, x, y)
