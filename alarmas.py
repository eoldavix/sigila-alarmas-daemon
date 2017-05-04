#!/usr/bin/env python
# coding=utf-8

""" TODO: Documentar """

import json
import requests
import mysql.connector as mysql
from config import Config
from logger import Logger

LOG = Logger().configure_logs()

class ServerNotFound(Exception):
    """ Excepción para servidores no encontrados """
    pass

class EventManager(object):
    """ Clase de manejo de eventos """

    def __init__(self):
        self.config = Config()
        self.all_events = self.config.events

    def get_payload(self, event, filters=None):
        """ Devuelve el payload que se pasará al webservice """

        filters = filters or None

        LOG.debug('Generando payload con event=%s y filters=%s', event, filters)

        try:
            myevent = self.config.get_event(event)

        except KeyError:
            return None

        string = myevent.string
        columns = myevent.columns

        query = "GET services\\nColumns: %s\\nFilter: description =" % columns

        filter_string = ""
        if filters:
            for myfilter in filters:
                filter_string += "Filter: %s\\n" % myfilter

        payload = '{\n'
        payload += ' "secret": "%s",\n' % self.config.webservice.key
        payload += ' "query": "%s %s\\n%s"\n' % (query, string, filter_string)
        payload += '}'

        LOG.debug('Devolviendo payload:\n%s', payload)

        return payload

    def call_webservice(self, server, payload):
        """ Ejecución de payload sobre un webservice """

        try:
            if server not in self.config.nagios_servers:
                raise ServerNotFound(server)

            url = 'http://%s:%s/%s' % (server,
                                       self.config.webservice.port,
                                       self.config.webservice.url
                                      )

            headers = {'Content-Type': '%s' % self.config.webservice.content_type}

            response = requests.post(url, payload, headers=headers)

            return json.dumps(response.text)

        except ServerNotFound as myerror:
            LOG.error("Servidor no encontrado: %s", myerror)

    def update_database(self, data):
        """ Método para actualizar la base de datos una vez obtenidos los datos
            desde el webservice """

        conn = mysql.connect(user=self.config.database['user'],
                             password=self.config.database['password'],
                             host=self.config.database['host'],
                             database=self.config.database['db']
                            )



def main():
    """ Main """
    eventmanager = EventManager()

    # for alarmas in eventmanager.all_events:
    #     print eventmanager.get_payload(alarmas)

    data = eventmanager.call_webservice('nagios-se', eventmanager.get_payload('dns'))
    eventmanager.update_database(data)

if __name__ == '__main__':
    main()
