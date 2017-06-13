![cga](http://cga.ced.junta-andalucia.es/portal/wp-content/uploads/2016/06/transparente.png?style=centerme)

# sigila-alarmas
Sincronización de Alarmas (Nagios) con Sigila.

# Requerimientos:

MySQL-python==1.2.5
pip==9.0.1
pycrypto==2.6.1
PyYAML==3.12
mysql-connector==2.1.4
schedule==0.4.2

# Instalación en servidor

```
git clone git@git.virt.cga:desarrollo/sigila-alarmas-daemon.git

cd sigila-alarmas-daemon
git checkout develop

apt-get install maridb-dev O libmysql...-dev
apt-get install python-dev
apt-get install build-essential
apt-get install libssl-dev
apt-get install libyaml-dev

pip install -r requirement.txt
```

# Creación de la tabla alarmas_daemon_events.
```
        CREATE TABLE IF NOT EXISTS `alarmas` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `ip_server` varchar(16) CHARACTER SET utf8 NOT NULL,
          `state_description` varchar(255) CHARACTER SET utf8 NOT NULL,
          `state` int(1) NOT NULL,
          `state_timestamp` timestamp NULL DEFAULT NULL,
          `check_timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (`id`),
          UNIQUE KEY `alarmas_index` (`ip_server`,`state_description`,`state`,`state_timestamp`)
        ) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

```
