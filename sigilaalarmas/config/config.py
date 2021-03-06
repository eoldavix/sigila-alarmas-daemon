#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Módulo de carga de configuración """

import os
from collections import namedtuple
import yaml
import mysql.connector as mysql

class Config(object):
    """ Carga la configuración desde el fichero config.yaml """
    def __init__(self):
        configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')

        with open(configfile, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)

            # database
            self.database = cfg['database']

            # nagios_servers
            self.nagios_servers = cfg['nagios_servers']['servers']
            self.webservice = namedtuple('Webservice',
                                         ['key', 'method', 'content_type', 'url'])
            self.webservice.key = cfg['nagios_servers']['key']
            self.webservice.method = cfg['nagios_servers']['method']
            self.webservice.content_type = cfg['nagios_servers']['content-type']
            self.webservice.url = cfg['nagios_servers']['url']
            self.webservice.port = cfg['nagios_servers']['port']

            # events
            self.events = cfg['events']
            self.event_priority_time = cfg['event_config']['priority_time']

            # logs
            self.logfile = cfg['logger']['file']
            self.loglevel = cfg['logger']['level']

    def  get_events_from_database(self):
        """ Carga la configuración de los eventos desde base de datos """

        conn = mysql.connect(user=self.database['user'],
                             password=self.database['password'],
                             host=self.database['host'],
                             database=self.database['db']
                            )

        cursor = conn.cursor()

        configtable = 'alarmas_daemon_eventconfig'

        sql = 'SELECT event, string, columns FROM %s;'

        raise NotImplementedError

    def show(self):
        """ Imprime la configuración en pantalla """
        print "Database config: %s" % self.database
        print "Nagios config: %s" % self.nagios_servers
        print "Event config: %s" % self.events

    def get_event(self, event):
        """ Devuelve la configuración de un evento """

        myevent = namedtuple('Event',
                             ['string', 'columns', 'priority', 'servers'])

        myevent.string = self.events[event]['string']
        myevent.columns = self.events[event]['columns']
        myevent.priority = self.events[event]['priority']
        myevent.servers = self.events[event]['servers']

        return myevent
