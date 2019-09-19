from elasticsearch import Elasticsearch

from src.utils.cadastro_logger import CadastroLogger

logger = CadastroLogger(__name__).logger


class ElasticSearchUtils:
    """Custom class for managing Elastic Search queries"""

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
        res = es.indices.create(index='cadaster', body=request_body)
        logger.debug(res)

    @staticmethod
    def remove_index():
        es = Elasticsearch()
        logger.debug("Deleting 'cadaster' index...")
        res = es.indices.delete(index='cadaster', ignore=[400, 404])
        logger.debug(res)
