from src.librecatastro.scrapping.format.scrapper_xml import ScrapperXML
from src.librecatastro.scrapping.input import Input


class ProvincesInput(Input):
    def __init__(self):
        super().__init__()

    @classmethod
    def scrap_provinces(cls, prov_list, scrapper=ScrapperXML):
        scrapper.scrap_provinces(prov_list)
