#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


class JSONEncoder(json.JSONEncoder):
    """
    Class that recursively encodes classes into json dictionaries
    """
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        else:
            return json.JSONEncoder.default(self, obj)
