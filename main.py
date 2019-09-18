import sys
import argparse

from src.librecatastro.scrapping.scrapper_html import ScrapperHTML
from src.librecatastro.scrapping.scrapper_xml import ScrapperXML

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs the Cadastro Parser')
    parser.add_argument('--coords', dest='coords', default=False, action='store_true')
    parser.add_argument('--filenames', action='store', nargs='+', dest='filenames', default=[])
    parser.add_argument('--provinces', action='store', nargs='+', dest='provinces', default=[])

    args = parser.parse_args(sys.argv[1:])
    if args.coords:
        ScrapperHTML.scrap_all_coordinates_files(args.filenames)
    else:
        ScrapperXML.scrap_all_addresses(args.provinces)
