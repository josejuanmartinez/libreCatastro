import re
from urllib.request import urlopen

from bs4 import BeautifulSoup

from src.librecatastro.domain.cadaster_entry.cadaster_entry_html import CadasterEntryHTML
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

'''Logger'''
logger = CadastroLogger(__name__).logger


class Scrapper:
    """Generic Scrapper class"""

    '''Catastro web services parametrized'''
    URL = "http://ovc.catastro.meh.es/ovcservweb/ovcswlocalizacionrc/ovccoordenadas.asmx/Consulta_RCCOOR?SRS=EPSG:4230&Coordenada_X={}&Coordenada_Y={}"
    URL_REF = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCListaBienes.aspx?rc1={}&rc2={}"
    URL_REF_FULL = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCConCiud.aspx?RefC={}&RCCompleta={}&del={}&mun={}"

    '''Information to scrap from HTML'''
    description_field_names = [u'Referencia catastral', u'Localización', u'Clase', u'Uso principal', u'Superficie construida', u'Año construcción']
    gsurface_field_names = [u'Superficie gráfica']

    def __init__(self):
        pass
