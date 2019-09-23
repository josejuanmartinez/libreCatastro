import unittest
from datetime import datetime
from time import sleep

from dotmap import DotMap

from src.librecatastro.domain.address import Address
from src.librecatastro.domain.cadaster_entry.cadaster_entry import CadasterEntry
from src.utils.elasticsearch_utils import ElasticSearchUtils


class ElasticSearchTests(unittest.TestCase):

    def setup_environment(self):
        ElasticSearchUtils.remove_index()
        sleep(5)
        ElasticSearchUtils.create_index()
        sleep(5)

    def insert_stores_document_in_elasticsearch(self):

        cadaster = DotMap()
        cadaster.address = Address("CL TESTTEST 17 03005 AJALVIR (MURCIA)")
        cadaster.cadaster = "AAAAA"
        cadaster.type = "Urbano"
        cadaster.use = "Religioso"
        cadaster.surface = "100m2"
        cadaster.year = "1970"
        cadaster.location = None
        cadaster.gsurface = "1200m2"
        cadaster.constructions = None
        cadaster.picture = None
        cadaster.timestamp = str(datetime.now())

        cadaster_entry = CadasterEntry(cadaster)

        cadaster_entry.to_elasticsearch()

        sleep(5)

        self.assertTrue(cadaster_entry.from_elasticsearch())

    def search_retrieves_document_from_elasticsearch(self):
        res = ElasticSearchUtils.check_if_address_present("CL TESTTEST 17", "AJALVIR", "MURCIA")
        self.assertTrue(res)

    def search_does_not_retrieve_document_from_elasticsearch(self):
        res = ElasticSearchUtils.check_if_address_present("CL TESTTEST 25", "AJALVIR", "MURCIA")
        self.assertFalse(res)

    def test_run_tests(self):
        self.setup_environment()
        self.insert_stores_document_in_elasticsearch()
        self.search_retrieves_document_from_elasticsearch()
        self.search_does_not_retrieve_document_from_elasticsearch()


if __name__ == '__main__':
    unittest.main()
