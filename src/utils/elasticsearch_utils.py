from elasticsearch import Elasticsearch


class ElasticSearchUtils:
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
                    }
                }
            }
        }
        print("Creating 'cadaster' index...")
        es.indices.create(index='cadaster', body=request_body)

    @staticmethod
    def remove_index():
        es = Elasticsearch()
        res = es.indices.delete(index='cadaster', ignore=[400, 404])
        print(res)