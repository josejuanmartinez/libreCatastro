import json

from datetime import datetime
from elasticsearch import Elasticsearch

from src.librecatastro.domain.address import Address
from src.librecatastro.domain.location import Location
from src.settings import config


class Cadaster:
    def __init__(self, dict):
        self.address = Address(dict[u'Localización'])
        self.cadaster = dict[u'Referencia catastral']
        self.type = dict[u'Clase'] if u'Clase' in dict else None
        self.use = dict[u'Uso principal'] if u'Uso principal' in dict else None
        self.surface = dict[u'Superficie construida'] if u'Superficie construida' in dict else None
        self.year = dict[u'Año construcción'] if u'Año construcción' in dict else None
        self.location = Location(dict[u'Longitud'], dict[u'Latitud']) if u'Longitud' in dict and u'Latitud' in dict else None
        self.timestamp = str(datetime.now())

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_elasticsearch(self):
        es = Elasticsearch()
        res = es.index(index=config['elasticsearch-index'], doc_type='cadaster_doc', id=self.cadaster, body=self.to_json())
        print(res)
        return res

    def from_elasticsearch(self):
        es = Elasticsearch()
        query = '{"query":{"bool":{"must":[{"match":{"cadaster":"' + self.cadaster + '"}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}'
        res = es.search(index=config['elasticsearch-index'], body=query)
        print(res)
        return res
