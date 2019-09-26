#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import abstractmethod


class Searcher:
    """ Just a signature, an abstract class just in case we need to define
    something common for Provinces and Coordinates Searchers """

    @abstractmethod
    def __init__(self):
        pass
