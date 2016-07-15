"""
Created on 01 March 2016
@description: Main application stub
@author: Tim Cavanagh
@modified: Tim Cavanagh 02 March 2016 tidied config
"""
from logging.config import dictConfig
import logging
import config
import pulldata

logger = logging.getLogger(__name__)

DEFAULT_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
}


def configure_logging(logfile_path):
    """
    Initialize logging defaults for Project.
    :param logfile_path: logfile used to the logfile
    :type logfile_path: string
    """
    dictConfig(DEFAULT_LOGGING)

    default_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] [%(funcName)s():%(lineno)s] %(message)s",
        "%d/%m/%Y %H:%M:%S")

    file_handler = logging.handlers.RotatingFileHandler(logfile_path, maxBytes=10485760, backupCount=300,
                                                        encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    file_handler.setFormatter(default_formatter)
    console_handler.setFormatter(default_formatter)

    logging.root.setLevel(logging.NOTSET)
    logging.root.addHandler(file_handler)
    logging.root.addHandler(console_handler)


def main():
    configure_logging(config.path_to_logs + 'pulldata.log')
    logger.info('App Started')
    pulldata.initialise()
    logger.info('App Finished')


if __name__ == '__main__':
    main()
