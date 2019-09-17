import sys

from src.librecatastro.catastro_scrapper import CadastroScrapper

if __name__ == "__main__":
    filename = ''
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    CadastroScrapper.scrap_all(filename)
