import logging
import logging.config
from logging.handlers import RotatingFileHandler

from src.settings import config


class CadastroLogger:
    """Custom logger for keeping track of the Catastro Scrapping"""

    def __init__(self, class_name):
        logging.config.fileConfig(fname=config['log_config'], defaults={'logfilename': config['log']}, disable_existing_loggers=False)

        self.logger = logging.getLogger(class_name)

        my_handler = RotatingFileHandler(config['log'], mode='a', maxBytes=5 * 1024 * 1024,
                                         backupCount=100, encoding='utf-8', delay=0)

        self.logger.addHandler(my_handler)
        pass

