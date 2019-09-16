import json

from datetime import datetime
from elasticsearch import Elasticsearch

from src.librecatastro.domain.address import Address
from src.librecatastro.domain.location import Location
from src.settings import config
from src.utils.cadastro_logger import CadastroLogger
from src.utils.json_enconder import JSONEncoder

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
        self.location = Location(description_data[u'Longitud'], description_data[u'Latitud'])
        self.timestamp = str(datetime.now())

    def to_json(self):
        return dict(address=self.address, cadaster=self.cadaster, type=self.type, use=self.use, surface=self.surface, year=self.year, location=self.location, timestamp=self.timestamp)

    def to_elasticsearch(self):
        es = Elasticsearch()
        body = json.dumps(self.to_json(), cls=JSONEncoder,sort_keys=True,
                  indent=4, separators=(',', ': '))
        logger.info("Sending to Elastic Search\n:{}".format(body))
        res = es.index(index=config['elasticsearch-index'], doc_type='cadaster_doc', id=self.cadaster, body=body)
        logger.info(res)
        return res

    def from_elasticsearch(self):
        es = Elasticsearch()
        query = '{"query":{"bool":{"must":[{"match":{"cadaster":"' + self.cadaster + '"}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}'
        res = es.search(index=config['elasticsearch-index'], body=query)
        logger.info(res)
        return res
