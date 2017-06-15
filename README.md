![cga](http://cga.ced.junta-andalucia.es/portal/wp-content/uploads/2016/06/transparente.png?style=centerme)

# sigila-alarmas
Sincronización de Alarmas (Nagios) con Sigila.

# Requerimientos:
```
MySQL-python==1.2.5
pip==9.0.1
pycrypto==2.6.1
PyYAML==3.12
mysql-connector==2.1.4
schedule==0.4.2
requests
```
# Tags
[develop](dockreg01.virt.cga/desarrollo/sigila-alarmas-daemon:develop): Versión de desarrollo  
[latest](dockreg01.virt.cga/desarrollo/sigila-alarmas-daemon:latest): Versión de producción

# Ejecución de stack
- En el directorio sigila-alarmas-daemon modificar el fichero .env
- Ejecutar `docker-compose up`  

# Ejecución de contenedor
## Variables pasadas como argumentos
```
docker run --rm -ti --name sigila-alarmas-daemon -e "DB_SERVER_HOST=ip_bbdd" -e "DB_SERVER_PORT=3306" -e "MYSQL_USER=usuario" -e "MYSQL_PASSWORD=contraseña" -e "MYSQL_DATABASE=basededatos" dockreg01.virt.cga/desarrollo/sigila-alarmas-daemon:latest
```

## Variables pasadas a través de archivo
```
docker run --rm -ti --name sigila-alarmas-daemon --env-file ./.env dockreg01.virt.cga/desarrollo/sigila-alarmas-daemon:latest
```


# Instalación y ejecución en servidor

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
python daemon.py start
```

# Configuración

Modificar los campos `database/host`, `database/user`, `database/password` y `database/db` de **sigilaalarmas/config/config.yaml** para la correcta configuración de la base de datos
