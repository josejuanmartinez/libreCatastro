import json
from datetime import datetime

from src.librecatastro.domain.address import Address
from src.librecatastro.domain.cadaster_entry.cadaster_entry import CadasterEntry
from src.librecatastro.domain.construction import Construction
from src.librecatastro.domain.location import Location
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

logger = CadastroLogger(__name__).logger


class CadasterEntryXML(CadasterEntry):
    """Cadaster class, that stores all the information about a surface and its properties"""

    def __init__(self,  xml, lon, lat):
        self.address = Address(xml['consulta_dnp']['bico']['bi']['ldt'])

        self.cadaster = xml['consulta_dnp']['bico']['bi']['idbi']['rc']['pc1'] + \
                   xml['consulta_dnp']['bico']['bi']['idbi']['rc']['pc2'] + \
                   xml['consulta_dnp']['bico']['bi']['idbi']['rc']['car'] + \
                   xml['consulta_dnp']['bico']['bi']['idbi']['rc']['cc1'] + \
                   xml['consulta_dnp']['bico']['bi']['idbi']['rc']['cc2']
        self.year = xml['consulta_dnp']['bico']['bi']['debi']['ant']

        type = xml['consulta_dnp']['bico']['bi']['idbi']['cn']
        self.type = u'Urbano' if type == 'UR' else u'Rústico'
        self.use = xml['consulta_dnp']['bico']['bi']['debi']['luso']
        self.surface = xml['consulta_dnp']['bico']['bi']['debi']['sfc'] + 'm2'
        self.year = xml['consulta_dnp']['bico']['bi']['debi']['ant']
        self.location = Location(lon, lat)
        self.gsurface = config['not_available_via_XML']
        self.constructions = []
        constructions = xml['consulta_dnp']['bico']['lcons']['cons']

        ''' Bad XML design, instead of returning a list with 1 element, it returns
        the element'''
        if not isinstance(constructions, list):
            constructions = [constructions]

        for construction in constructions:
            use = construction['lcd']
            doorway = construction['dt']['lourb']['loint']['es']
            floor = construction['dt']['lourb']['loint']['pt']
            door = construction['dt']['lourb']['loint']['pt']
            surface = construction['dfcons']['stl']
            reform_type = config['not_available_via_XML']
            reform_date = config['not_available_via_XML']

            self.constructions.append(Construction(dict(uso=use, escalera=doorway, planta=floor, puerta=door, superficie=surface, tipo=reform_type, fecha=reform_date)))

        self.timestamp = str(datetime.now())
        super().__init__(self)





