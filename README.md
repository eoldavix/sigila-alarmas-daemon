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

# Configuración

Modificar los campos `database/host`, `database/user`, `database/password` y `database/db` de **sigilaalarmas/config/config.yaml** para la correcta configuración de la base de datos
