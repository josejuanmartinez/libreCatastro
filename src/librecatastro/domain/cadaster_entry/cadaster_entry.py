#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from abc import abstractmethod

from dotmap import DotMap
from elasticsearch import Elasticsearch

from src.settings import config
from src.utils.catastro_logger import CadastroLogger
from src.utils.json_encoder import JSONEncoder

'''Logger'''
logger = CadastroLogger(__name__).logger


class CadasterEntry:
    """ Parent class that stores information about an entry in the Cadaster.
     It's instantiated from children classes (CadasterEntryHTML and CadasterEntryXML,
     not directly"""
    @abstractmethod
    def __init__(self, cadaster_entry):
        self.address = cadaster_entry.address
        self.cadaster = cadaster_entry.cadaster
        self.type = cadaster_entry.type
        self.use = cadaster_entry.use
        self.surface = cadaster_entry.surface
        self.year = cadaster_entry.year
        self.location = cadaster_entry.location
        self.gsurface = cadaster_entry.gsurface
        self.constructions = cadaster_entry.constructions
        self.picture = cadaster_entry.picture
        self.timestamp = cadaster_entry.timestamp
        logger.debug(self.to_json_recursive())

    def to_json(self):
        """ Transforms an object of this class into a json dict """
        return dict(address=self.address, cadaster=self.cadaster, type=self.type, use=self.use, surface=self.surface, year=self.year, location=self.location, gsurface=self.gsurface, constructions=self.constructions, picture=str(self.picture) if self.picture is not None else None, timestamp=self.timestamp)

    def to_json_recursive(self):
        """ Transforms recursively this object and all the objects inside that implement to_json() """
        return json.dumps(self.to_json(), cls=JSONEncoder, sort_keys=True,
                          indent=4, separators=(',', ': '))

    def to_elasticsearch(self):
        """ Gets stored in elastic search """
        es = Elasticsearch(hosts=[config['elasticsearch-host']], port=config['elasticsearch-port'],
                           http_auth=(config['elasticsearch-user'], config['elasticsearch-pass']))
        res = None
        try:
            body = json.dumps(self.to_json(), cls=JSONEncoder,sort_keys=True,
                    indent=4, separators=(',', ': '))
            res = es.index(index=config['elasticsearch-index'], doc_type='_doc', id=self.cadaster, body=body)
        except Exception as e:
            logger.error(e)

        es.transport.close()

        return res

    def from_elasticsearch(self):
        """ Confirms for checking purposes that the entry has been stored in elastic search previously """
        res = False
        es = Elasticsearch(hosts=[config['elasticsearch-host']], port=config['elasticsearch-port'],
                           http_auth=(config['elasticsearch-user'], config['elasticsearch-pass']))
        try:
            query = '{"query":{"bool":{"must":[{"match":{"cadaster":"' + self.cadaster + '"}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}'
            res = es.search(index=config['elasticsearch-index'], body=query)
            hits = DotMap(res).hits.total
            if hits == DotMap():
                hits = 0
            res = (hits > 0)
        except Exception as e:
            logger.error(e)

        es.transport.close()

        return res
