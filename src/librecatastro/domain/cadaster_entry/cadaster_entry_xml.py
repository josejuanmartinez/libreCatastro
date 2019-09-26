#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from dotmap import DotMap

from src.librecatastro.domain.address import Address
from src.librecatastro.domain.cadaster_entry.cadaster_entry import CadasterEntry
from src.librecatastro.domain.construction import Construction
from src.librecatastro.domain.location import Location
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

logger = CadastroLogger(__name__).logger


class CadasterEntryXML(CadasterEntry):
    """Cadaster class, obtained from parsing XML, that inheritates from Cadaster, and
     stores all the information about a surface and its properties"""

    def __init__(self,  xml, lon=None, lat=None, picture=None):
        self.address = None
        if xml.consulta_dnp.bico.bi.ldt != DotMap():
            self.address = Address(xml.consulta_dnp.bico.bi.ldt)

        self.cadaster  = xml.consulta_dnp.bico.bi.idbi.rc.pc1 if xml.consulta_dnp.bico.bi.idbi.rc.pc1 != DotMap() else ''
        self.cadaster += xml.consulta_dnp.bico.bi.idbi.rc.pc2 if xml.consulta_dnp.bico.bi.idbi.rc.pc2 != DotMap() else ''
        self.cadaster += xml.consulta_dnp.bico.bi.idbi.rc.car if xml.consulta_dnp.bico.bi.idbi.rc.car != DotMap() else ''
        self.cadaster += xml.consulta_dnp.bico.bi.idbi.rc.cc1 if xml.consulta_dnp.bico.bi.idbi.rc.cc1 != DotMap() else ''
        self.cadaster += xml.consulta_dnp.bico.bi.idbi.rc.cc2 if xml.consulta_dnp.bico.bi.idbi.rc.cc2 != DotMap() else ''

        self.year = None
        if xml.consulta_dnp.bico.bi.debi is not None:
            self.year = xml.consulta_dnp.bico.bi.debi.ant
            if self.year == DotMap():
                self.year = None

        self.type = xml.consulta_dnp.bico.bi.idbi.cn
        if self.type != DotMap() and self.type == 'UR':
            self.type = u'Urbano'
        else:
            self.type = u'Rústico'

        self.use = None
        if xml.consulta_dnp.bico.bi.debi is not None:
            self.use = xml.consulta_dnp.bico.bi.debi.luso
            if self.use == DotMap():
                self.use = None

        self.surface = None
        if xml.consulta_dnp.bico.bi.debi is not None:
            self.surface = xml.consulta_dnp.bico.bi.debi.sfc + 'm2'
            if self.surface == DotMap():
                self.surface = None

        self.location = Location(lon, lat)
        self.gsurface = config['not_available_via_XML']
        self.constructions = []

        constructions = []
        if xml.consulta_dnp.bico.lcons.cons != DotMap():
            constructions = xml.consulta_dnp.bico.lcons.cons

        ''' Bad XML design, instead of returning a list with 1 element, it returns
        the element'''
        if not isinstance(constructions, list):
            constructions = [constructions]

        for construction in constructions:
            use = construction.lcd
            if use == DotMap():
                use = None

            doorway = construction.dt.lourb.loint.es
            if doorway == DotMap():
                doorway = None

            floor = construction.dt.lourb.loint.pt
            if floor == DotMap():
                floor = None

            door = construction.dt.lourb.loint.pu
            if door == DotMap():
                door = None

            surface = construction.dfcons.stl
            if surface == DotMap():
                surface = None

            reform_type = config['not_available_via_XML']
            reform_date = config['not_available_via_XML']

            self.constructions.append(Construction(
                dict(uso=use, escalera=doorway, planta=floor, puerta=door, superficie=surface, tipo=reform_type,
                     fecha=reform_date)))

        self.picture = picture
        self.timestamp = str(datetime.now())
        super().__init__(self)
