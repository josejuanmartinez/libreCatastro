#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dotmap import DotMap
from elasticsearch import Elasticsearch

from src.settings import config
from src.utils.catastro_logger import CadastroLogger

logger = CadastroLogger(__name__).logger


class ElasticSearchUtils:
    """Custom class for managing Elastic Searcher queries"""

    def __init__(self):
        pass

    @staticmethod
    def create_index():
        """
        Creates index in ElasticSearch
        """
        ElasticSearchUtils.remove_index()
        es = Elasticsearch(hosts=[config['elasticsearch-host']], port=config['elasticsearch-port'],
                           http_auth=(config['elasticsearch-user'], config['elasticsearch-pass']))
        request_body = {
            "settings": {
                "number_of_shards": 5,
                "number_of_replicas": 1
            },

            "mappings": {
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
        logger.debug("Creating 'cadaster' index...")
        try:
            res = es.indices.create(index='cadaster', body=request_body)
            logger.debug(res)
        except Exception as e:
            logger.debug(e)

        es.transport.close()

    @staticmethod
    def remove_index():
        """
        Removes index from ElasticSearch
        """
        es = Elasticsearch(hosts=[config['elasticsearch-host']], port=config['elasticsearch-port'],
                           http_auth=(config['elasticsearch-user'], config['elasticsearch-pass']))
        logger.debug("Deleting 'cadaster' index...")
        try:
            res = es.indices.delete(index='cadaster', ignore=[400, 404])
            logger.debug(res)
        except Exception as e:
            logger.debug(e)

        es.transport.close()

    @staticmethod
    def check_if_address_present(address, city_name, province_name):
        """
        Checks if an address has been already scrapped (to skip it).
        :param address: full addres (including tipo de via, nombre de via ...)
        :param city_name: City Name
        :param province_name: Province Name
        :return: True if already scrapped, False otherwise
        """
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
        es = Elasticsearch(hosts=[config['elasticsearch-host']], port=config['elasticsearch-port'],
                           http_auth=(config['elasticsearch-user'], config['elasticsearch-pass']))
        try:
            res = es.search(index=config['elasticsearch-index'], body=query)
            hits = res['hits']['total']['value']
            res = (hits > 0)
        except Exception as e:
            logger.debug(e)

        es.transport.close()

        return res

