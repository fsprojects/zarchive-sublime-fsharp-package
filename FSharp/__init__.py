import os
import sys
import logging
import logging.handlers
import logging.config


LOGGER_PATH = os.path.join(os.path.dirname(__file__), 'fsharp.log')


logger = logging.getLogger('FSharp')
logger.setLevel(logging.ERROR)

handler = logging.handlers.RotatingFileHandler(LOGGER_PATH, 'a', 2**13)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter(fmt='%(asctime)s - %(name)s:%(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(formatter)

# ST may reload this file multiple times and `logging` keeps adding handlers.
logger.handlers = []
logger.addHandler(handler)

logger.debug('top-level logger initialized')
