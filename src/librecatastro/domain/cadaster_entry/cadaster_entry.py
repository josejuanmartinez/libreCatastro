import json
from abc import abstractmethod

from elasticsearch import Elasticsearch

from src.settings import config
from src.utils.cadastro_logger import CadastroLogger
from src.utils.json_encoder import JSONEncoder

'''Logger'''
logger = CadastroLogger(__name__).logger


class CadasterEntry:

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
        self.timestamp = cadaster_entry.timestamp

    def to_json(self):
        return dict(address=self.address, cadaster=self.cadaster, type=self.type, use=self.use, surface=self.surface, year=self.year, location=self.location, gsurface=self.gsurface, constructions=self.constructions, timestamp=self.timestamp)

    def to_json_recursive(self):
        return json.dumps(self.to_json(), cls=JSONEncoder, sort_keys=True,
                          indent=4, separators=(',', ': '))

    def to_elasticsearch(self):
        try:
            es = Elasticsearch()
            body = json.dumps(self.to_json(), cls=JSONEncoder,sort_keys=True,
                    indent=4, separators=(',', ': '))
        #logger.debug("Sending to Elastic Search\n:{}".format(body))
            res = es.index(index=config['elasticsearch-index'], doc_type='cadaster_doc', id=self.cadaster, body=body)
        #logger.debug(res)
        except Exception as e:
            logger.error(e)
        finally:
            es.transport.close()

        return res

    def from_elasticsearch(self):
        res = None

        try:
            es = Elasticsearch()
            query = '{"query":{"bool":{"must":[{"match":{"cadaster":"' + self.cadaster + '"}}],"must_not":[],"should":[]}},"from":0,"size":10,"sort":[],"aggs":{}}'
            res = es.search(index=config['elasticsearch-index'], body=query)
        except Exception as e:
            logger.error(e)
        finally:
            es.transport.close()

        return res
