from dotmap import DotMap
from elasticsearch import Elasticsearch

from src.settings import config
from src.utils.cadastro_logger import CadastroLogger

logger = CadastroLogger(__name__).logger


class ElasticSearchUtils:
    """Custom class for managing Elastic Searcher queries"""

    def __init__(self):
        pass

    @staticmethod
    def create_index():
        ElasticSearchUtils.remove_index()
        es = Elasticsearch()
        request_body = {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 1
            },

            "mappings": {
                "cadaster_doc": {
                    "properties": {
                        "location": {
                            "type": "geo_point"
                        },
                        "constructions": {
                            "type": "nested",
                            "properties":
                            {
                                "door": {"type": "keyword"},
                                "doorway": {"type": "keyword"},
                                "floor": {"type": "keyword"},
                                "reform": {
                                    "type": "nested",
                                    "properties":
                                        {
                                            "type": {"type": "keyword"},
                                            "year": {"type": "keyword"},
                                        }
                                },
                                "surface": {"type": "keyword"},
                                "use": {"type": "keyword"}
                            }
                        }
                    },
                    "dynamic_templates": [
                        {
                            "strings": {
                                "match_mapping_type": "string",
                                "mapping": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword"
                                        }
                                    }
                                }
                            }
                        }
                    ]
                },
            }
        }
        logger.debug("Creating 'cadaster' index...")
        try:
            res = es.indices.create(index='cadaster', body=request_body)
            logger.debug(res)
        except Exception as e:
            logger.debug(e)

        es.transport.close()

    @staticmethod
    def remove_index():
        es = Elasticsearch()
        logger.debug("Deleting 'cadaster' index...")
        try:
            res = es.indices.delete(index='cadaster', ignore=[400, 404])
            logger.debug(res)
        except Exception as e:
            logger.debug(e)

        es.transport.close()

    @staticmethod
    def check_if_address_present(address, city_name, province_name):
        res = False
        query = {"query":
                     {"bool":
                          {"must":
                               [{"prefix":
                                     {"address.full_address.keyword":"{}".format(address)}},
                                {"match":
                                     {"address.province.keyword":"{}".format(province_name)}},
                                {"match":{"address.city.keyword":"{}".format(city_name)}}],
                           "must_not":[],
                           "should":[]}},
                 "from":0,
                 "size":11,
                 "sort":[],
                 "aggs":{}}
        es = Elasticsearch()
        try:
            res = es.search(config['elasticsearch-index'], config['elasticsearch-doc'], query)
            print(query)
            hits = DotMap(res).hits.total
            if hits == DotMap():
                hits = 0
            res = (hits > 0)
            logger.debug("Found in ES: {}".format(hits))
        except Exception as e:
            logger.debug(e)

        es.transport.close()

        return res

