#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ListUtils:
    """ Different functions for make working with lists easier"""
    def __init__(self):
        pass

    @staticmethod
    def flat(non_flat_list):
        """
        Flattens a multilevel list [[], []...] -> [, , , ]
        :param non_flat_list: Multilevel list
        :return: A flattened list
        """
        return [item for sublist in non_flat_list for item in sublist]
