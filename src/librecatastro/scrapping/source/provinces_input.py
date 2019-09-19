from src.librecatastro.scrapping.input import Input


class ProvincesInput(Input):
    def __init__(self):
        super().__init__()

    @classmethod
    def scrap_provinces(cls, scrapper, prov_list, pictures=False):
        scrapper.scrap_provinces(prov_list, pictures)
