#!/usr/bin/env python
# coding=utf-8

""" TODO: Documentar """

import json
import datetime
import time
import requests
import schedule
import mysql.connector as mysql
from ..config.config import Config
from ..config.logger import Logger

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
        # servers = myevent.servers

        query = "GET services\\nColumns: %s\\nFilter: description =" % columns

        # filter_string = ''.join("Filter: host_name ~ %s\\n" % x for x in servers)
        if filters:
            filter_string = ''.join("Filter: %s\\n" % x for x in filters)
            # for myfilter in filters:
                # filter_string += "Filter: %s\\n" % myfilter

        payload = '{\n'
        payload += ' "secret": "%s",\n' % self.config.webservice.key
        payload += ' "query": "%s %s\\n%s"\n' % (query, string, filter_string)
        payload += '}'

        LOG.debug('Devolviendo payload:\n%s', payload)

        return payload

    def init_database(self):
        """ Inicializa la base de datos """
        query = """
        CREATE TABLE IF NOT EXISTS `alarmas_daemon_events` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `ip_server` varchar(16) CHARACTER SET utf8 NOT NULL,
          `id_fk_tipo_alarmas` int(5) NOT NULL,
          `state` int(1) NOT NULL,
          `state_timestamp` int(11) NULL DEFAULT NULL,
          `check_timestamp` int(11) NULL DEFAULT NULL,
          `id_fk_operadores` varchar(15) NULL DEFAULT NULL,
          `revisada` int(1) NOT NULL DEFAULT 0,
          PRIMARY KEY (`id`),
          UNIQUE KEY `alarmas_daemon_events_index` (`ip_server`,`id_fk_tipo_alarmas`,`state`,`state_timestamp`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8; """

        conn = mysql.connect(user=self.config.database['user'],
                             password=self.config.database['password'],
                             host=self.config.database['host'],
                             database=self.config.database['db']
                            )

        cursor = conn.cursor()

        cursor.execute(query)

        try:
            conn.commit()
        except mysql.Error as myerror:
            LOG.error("Excepción encontrada: %s", myerror)
        finally:
            cursor.close()
            conn.close()

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
            query = ('INSERT INTO alarmas_daemon_events '
                     '(id_fk_tipo_alarmas, ip_server, state, state_timestamp, check_timestamp) '
                     'SELECT id, "%s", "%i", "%s", UNIX_TIMESTAMP()  '
                     'FROM alarmas_tipo '
                     'WHERE nombre = "%s" '
                     'ON DUPLICATE KEY UPDATE '
                     '`check_timestamp` = UNIX_TIMESTAMP();\n'
                    )

            # st_ts = datetime.datetime.fromtimestamp(int(row[3])
            #                                        ).strftime('%Y-%m-%d %H:%M:%S')

            try:
                cursor.execute(query % (row[0],
                                        row[2],
                                        row[3],
                                        row[1],
                                       ))
            except mysql.errors.ProgrammingError:
                # En caso de error, se inicializa la base de datos
                self.init_database()


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
                for srv in myevent.servers:
                    payload = self.get_payload(event, ["host_name ~ %s" % srv])
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
            schedule.every(int(minutes)).minutes.do(self.execute_with_priority, priority)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def execute_all(self):
        """ Método para la ejecución de todos los eventos
            sobre todos los servidores. """

        LOG.info("Realizando actualización de todos los eventos")
        for event in self.config.events:
            LOG.info("Actualizando base de datos para evento %s", event)
            myevent = self.config.get_event(event)
            for srv in myevent.servers:
                payload = self.get_payload(event, ["host_name ~ %s" % srv])
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
