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

    def __init__(self, xml, lon, lat, is_property=True):

        self.address = Address(xml['consulta_dnp']['bico']['bi']['ldt'])

        self.cadaster = xml['consulta_dnp']['bico']['bi']['idbi']['rc']['pc1'] + \
                        xml['consulta_dnp']['bico']['bi']['idbi']['rc']['pc2'] + \
                        xml['consulta_dnp']['bico']['bi']['idbi']['rc']['car'] + \
                        xml['consulta_dnp']['bico']['bi']['idbi']['rc']['cc1'] + \
                        xml['consulta_dnp']['bico']['bi']['idbi']['rc']['cc2']

        self.year = xml['consulta_dnp']['bico']['bi']['debi']['ant'] \
            if 'debi' in xml['consulta_dnp']['bico']['bi'] and\
               'ant' in xml['consulta_dnp']['bico']['bi']['debi'] else None

        self.type = xml['consulta_dnp']['bico']['bi']['idbi']['cn'] if 'cn' in xml['consulta_dnp']['bico']['bi']['idbi'] else None
        if self.type is not None:
            self.type = u'Urbano' if self.type == 'UR' else u'Rústico'

        self.use = xml['consulta_dnp']['bico']['bi']['debi']['luso'] if 'luso' in xml['consulta_dnp']['bico']['bi']['debi'] else None
        self.surface = xml['consulta_dnp']['bico']['bi']['debi']['sfc'] + 'm2' if 'sfc' in xml['consulta_dnp']['bico']['bi']['debi'] else None
        self.location = Location(lon, lat)
        self.gsurface = config['not_available_via_XML']
        self.constructions = []

        constructions = []
        if 'lcons' in xml['consulta_dnp']['bico']:
            constructions = xml['consulta_dnp']['bico']['lcons']['cons']

        ''' Bad XML design, instead of returning a list with 1 element, it returns
        the element'''
        if not isinstance(constructions, list):
            constructions = [constructions]

        for construction in constructions:
            use = construction['lcd'] if 'lcd' in construction else None
            doorway = construction['dt']['lourb']['loint']['es'] if 'dt' in construction else None
            floor = construction['dt']['lourb']['loint']['pt'] if 'dt' in construction else None
            door = construction['dt']['lourb']['loint']['pu'] if 'dt' in construction else None
            surface = construction['dfcons']['stl'] if 'dfcons' in construction and 'stl' in construction['dfcons'] else None
            reform_type = config['not_available_via_XML']
            reform_date = config['not_available_via_XML']

            self.constructions.append(Construction(
                dict(uso=use, escalera=doorway, planta=floor, puerta=door, superficie=surface, tipo=reform_type,
                     fecha=reform_date)))

        self.timestamp = str(datetime.now())
        super().__init__(self)
