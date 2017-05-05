#!/usr/bin/env python
# coding=utf-8

""" TODO: Documentar """

import json
import datetime
import time
import requests
import schedule
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

            return response.text

        except ServerNotFound as myerror:
            LOG.error("Servidor no encontrado: %s", myerror)

    def update_database(self, data):
        """ Método para actualizar la base de datos una vez obtenidos los datos
            desde el webservice. Recibe los datos en raw. """

        data = json.loads(data)

        conn = mysql.connect(user=self.config.database['user'],
                             password=self.config.database['password'],
                             host=self.config.database['host'],
                             database=self.config.database['db']
                            )

        cursor = conn.cursor()

        LOG.debug("Actualizando base de datos. Insertando %i filas. ", len(data))

        for row in data:
            query = ('INSERT INTO alarmas '
                     '(ip_server, state_description, state, state_timestamp) '
                     'VALUES ("%s", "%s", "%i", "%s") '
                     'ON DUPLICATE KEY UPDATE '
                     '`check_timestamp` = NOW();\n'
                    )

            st_ts = datetime.datetime.fromtimestamp(int(row[3])
                                                   ).strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute(query % (row[0],
                                    row[1],
                                    row[2],
                                    st_ts
                                   ))

        try:
            conn.commit()
        except mysql.Error as myerror:
            LOG.error("Excepción encontrada: %s", myerror)
        finally:
            cursor.close()
            conn.close()

    def execute_with_priority(self, priority):
        """ Método para la ejecución de todos los eventos
            con una prioridad pasada sobre todos los servidores. """

        LOG.debug("Ejecutando eventos con prioridad %s", priority)
        for event in self.config.events:
            myevent = self.config.get_event(event)
            if myevent.priority == priority:
                LOG.debug("Evento %s encontrado con prioridad %s", myevent.string, priority)
                payload = self.get_payload(event)
                for server in self.config.nagios_servers:
                    LOG.debug("Solicitando datos del evento %s en servidor %s",
                              myevent.string,
                              server
                             )
                    data = self.call_webservice(server, payload)
                    try:
                        self.update_database(data)
                    except ValueError:
                        msg = "Error al intentar actualizar base de datos. "
                        msg += "Servidor: %s. Evento: %s" % (server, event)
                        LOG.error(msg)

    def events_scheduling(self):
        """ Programación de las ejecuciones según el tiempo establecido """
        for priority in self.config.event_priority_time:
            LOG.debug("Ejecutando por primera vez con prioridad %s", priority)
            self.execute_with_priority(priority)
            minutes = self.config.event_priority_time[priority]
            LOG.debug("Configurando programación de prioridad %s cada %s minutos",
                      priority,
                      minutes
                     )
            schedule.every(int(minutes)).seconds.do(self.execute_with_priority, priority)

        while True:
            schedule.run_pending()
            time.sleep(1)

def main():
    """ Main """
    eventmanager = EventManager()

    # data = eventmanager.call_webservice('nagios-se', eventmanager.get_payload('dns'))
    # eventmanager.update_database(data)

    # eventmanager.execute_with_priority(1)
    eventmanager.events_scheduling()

if __name__ == '__main__':
    main()
