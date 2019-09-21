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
    """HTML Catastro Scrapper"""

    URL = "http://ovc.catastro.meh.es/ovcservweb/ovcswlocalizacionrc/ovccoordenadas.asmx/Consulta_RCCOOR?SRS=EPSG:4226&Coordenada_X={}&Coordenada_Y={}"
    URL_REF = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCListaBienes.aspx?rc1={}&rc2={}"
    URL_REF_FULL = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?RefC={}&RCCompleta={}&del={}&mun={}"

    def __init__(self):
        super().__init__()

    @classmethod
    def scrap_coord(cls, x, y):
        logger.debug("====Longitude: {} Latitude: {}====".format(x, y))
        url = cls.URL.format(x, y)
        logger.debug("URL for coordinates: {}".format(url))
        f = urlopen(url)

        sleep(config['sleep_time'])
        return f.read()

    @classmethod
    def scrap_cadaster_full_code(cls, full_cadaster, delimitacion, municipio):
        url_ref = cls.URL_REF_FULL.format(full_cadaster, full_cadaster, delimitacion, municipio)
        logger.debug("-->FULL URL for cadastral data: {}".format(url_ref))
        f_ref = urlopen(url_ref)
        data_ref = f_ref.read()
        html = str(data_ref.decode('utf-8'))
        parsed_html = BeautifulSoup(html, features="html.parser")

        sleep(config['sleep_time'])
        return parsed_html

    @classmethod
    def scrap_cadaster(cls, cadaster, delimitacion=None, municipio=None, pictures=False):
        rc_1 = cadaster[0:7]
        rc_2 = cadaster[7:14]
        url_ref = cls.URL_REF.format(rc_1, rc_2)

        logger.debug("URL for cadastral data: {}".format(url_ref))

        f_ref = urlopen(url_ref)
        data_ref = f_ref.read()
        sleep(config['sleep_time'])

        html = str(data_ref.decode('utf-8'))
        parsed_html = BeautifulSoup(html, features="html.parser")

        if delimitacion is None:
            delimitacion_search = re.search(r'del=([0-9]+)&', html)
            if delimitacion_search:
                delimitacion = delimitacion_search.group(1)

        if municipio is None:
            municipio_search = re.search(r'mun=([0-9]+)&', html)
            if municipio_search:
                municipio = municipio_search.group(1)

        description = parsed_html.find(id='ctl00_Contenido_tblInmueble')

        picture = None
        if pictures:
            picture = cls.scrap_site_picture(delimitacion, municipio, ''.join([rc_1, rc_2]))
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
                parsed_html = ScrapperHTML.scrap_cadaster_full_code(partial_cadaster_text, delimitacion, municipio)
                htmls.append((parsed_html, picture))
                sleep(config['sleep_time'])
        else:
            # Parcela
            htmls.append((parsed_html, picture))

        return htmls

