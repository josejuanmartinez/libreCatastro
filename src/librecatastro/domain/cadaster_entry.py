import json

from datetime import datetime
from elasticsearch import Elasticsearch

from src.librecatastro.domain.address import Address
from src.librecatastro.domain.location import Location
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

logger = CadastroLogger(__name__).logger


class CadasterEntry:
    """Cadaster class, that stores all the information about a surface and its properties"""

    def __init__(self, description_data):
        self.address = Address(description_data[u'Localización'])
        self.cadaster = description_data[u'Referencia catastral']
        self.type = description_data[u'Clase'] if u'Clase' in description_data else None
        self.use = description_data[u'Uso principal'] if u'Uso principal' in description_data else None
        self.surface = description_data[u'Superficie construida'] if u'Superficie construida' in description_data else None
        self.year = description_data[u'Año construcción'] if u'Año construcción' in description_data else None
        self.location = Location(description_data[u'Longitud'], description_data[u'Latitud']) if u'Longitud' in description_data and u'Latitud' in description_data else None
        self.timestamp = str(datetime.now())

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_elasticsearch(self):
        es = Elasticsearch()
        res = es.index(index=config['elasticsearch-index'], doc_type='cadaster_doc', id=self.cadaster, body=self.to_json())
        logger.info(res)
        return res

    def from_elasticsearch(self):
        es = Elasticsearch()
        query = '{"query":{"bool":{"must":[{"match":{"cadaster":"' + self.cadaster + '"}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}'
        res = es.search(index=config['elasticsearch-index'], body=query)
        logger.info(res)
        return res
