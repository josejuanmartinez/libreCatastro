#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script that initializes 'cadaster' index in ElasticSearch so that
is also well supported by Kibana Visualization """

from src.utils.elasticsearch_utils import ElasticSearchUtils

if __name__ == "__main__":
    ElasticSearchUtils.create_index()
