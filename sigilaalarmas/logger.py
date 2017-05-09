#!/usr/bin/env python
# coding=utf-8

""" Configura los logs """

import logging
from config import Config

LEVEL = logging.getLevelName(Config().loglevel)
LOGFILE = Config().logfile

class Logger(object):
    """ Clase para la configuración de los logs """

    def __init__(self, level=LEVEL):
        self.logger = logging.getLogger('sigila-alarmas')
        self.logger.setLevel(logging.DEBUG)
        filelog = logging.FileHandler(LOGFILE)
        filelog.setLevel(logging.DEBUG)
        consolelog = logging.StreamHandler()
        consolelog.setLevel(level)
        # create formatter and add it to the handlers
        longformatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        shortformatter = logging.Formatter('%(message)s')
        filelog.setFormatter(longformatter)
        consolelog.setFormatter(shortformatter)
        self.logger.addHandler(filelog)
        self.logger.addHandler(consolelog)

    def configure_logs(self):
        """ Devuelve en una variable el logger """
        return self.logger
