import sys
import argparse

from src.librecatastro.scrapping.format.scrapper_html import ScrapperHTML
from src.librecatastro.scrapping.format.scrapper_xml import ScrapperXML
from src.librecatastro.scrapping.source.coordinates_input import CoordinatesInput
from src.librecatastro.scrapping.source.provinces_input import ProvincesInput
from src.settings import config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs the Cadastro Parser')
    parser.add_argument('--coords', dest='coords', default=False, action='store_true')
    parser.add_argument('--filenames', action='store', nargs='+', dest='filenames', default=[])
    parser.add_argument('--provinces', action='store', nargs='+', dest='provinces', default=[])
    parser.add_argument('--sleep', action='store', dest='sleep', type=int, default=5)
    parser.add_argument('--html', dest='html', default=False, action='store_true')
    parser.add_argument('--scale', action='store', dest='scale', type=int, default=10000)

    args = parser.parse_args(sys.argv[1:])

    if args.sleep:
        config['sleep_time'] = args.sleep

    if args.scale:
        config['scale'] = args.scale

    scrapper = ScrapperHTML if args.html else ScrapperXML

    if args.coords:
        CoordinatesInput.scrap_coordinates(args.filenames, scrapper)
    else:
        ProvincesInput.scrap_provinces(args.provinces, scrapper)
