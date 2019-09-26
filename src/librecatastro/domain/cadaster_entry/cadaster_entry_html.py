#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from src.librecatastro.domain.address import Address
from src.librecatastro.domain.cadaster_entry.cadaster_entry import CadasterEntry
from src.librecatastro.domain.construction import Construction
from src.librecatastro.domain.location import Location
from src.utils.cadastro_logger import CadastroLogger

logger = CadastroLogger(__name__).logger


class CadasterEntryHTML(CadasterEntry):
    """Cadaster class, obtained from parsing HTML, that inheritates from Cadaster, and
     stores all the information about a surface and its properties"""

    def __init__(self, description_data):
        self.address = Address(description_data[u'Localización'])
        self.cadaster = description_data[u'Referencia catastral']
        self.type = description_data[u'Clase'] if u'Clase' in description_data else None
        self.use = description_data[u'Uso principal'] if u'Uso principal' in description_data else None
        self.surface = description_data[u'Superficie construida'] if u'Superficie construida' in description_data else None
        self.year = description_data[u'Año construcción'] if u'Año construcción' in description_data else None
        self.location = Location(description_data[u'Longitud'], description_data[u'Latitud'])
        self.gsurface = description_data[u'Superficie gráfica'] if u'Superficie gráfica' in description_data else None
        self.constructions = [Construction(x) for x in description_data[u'Construcciones']]
        self.picture = description_data[u'GráficoParcela'] if u'GráficoParcela' in description_data else None
        self.timestamp = str(datetime.now())
        super().__init__(self)

