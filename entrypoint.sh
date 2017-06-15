#!/bin/ash

set +e

# Script trace mode
if [ "${DEBUG_MODE}" == "true" ]; then
    set -o xtrace
fi

# Default timezone for web interface
TZ=${TZ:-"Europe/Madrid"}

# Check prerequisites for MySQL database
check_variables_mysql() {
    DB_SERVER_HOST=${DB_SERVER_HOST:-"mysql-server"}
    DB_SERVER_PORT=${DB_SERVER_PORT:-"3306"}
    USE_DB_ROOT_USER=false
    CREATE_DB_USER=false

    if [ ! -n "${MYSQL_USER}" ] && [ "${MYSQL_RANDOM_ROOT_PASSWORD}" == "true" ]; then
        echo "**** Impossible to use MySQL server because of unknown user and random 'root' password"
        exit 1
    fi

    if [ ! -n "${MYSQL_USER}" ] && [ ! -n "${MYSQL_ROOT_PASSWORD}" ] && [ "${MYSQL_ALLOW_EMPTY_PASSWORD}" != "true" ]; then
        echo "*** Impossible to use MySQL server because 'root' password is not defined and not empty"
        exit 1
    fi

    if [ "${MYSQL_ALLOW_EMPTY_PASSWORD}" == "true" ] || [ -n "${MYSQL_ROOT_PASSWORD}" ]; then
        USE_DB_ROOT_USER=true
        DB_SERVER_ROOT_USER="root"
        DB_SERVER_ROOT_PASS=${MYSQL_ROOT_PASSWORD:-""}
    fi

    [ -n "${MYSQL_USER}" ] || CREATE_DB_USER=true

    # If root password is not specified use provided credentials
    DB_SERVER_ROOT_USER=${DB_SERVER_ROOT_USER:-${MYSQL_USER}}
    [ "${MYSQL_ALLOW_EMPTY_PASSWORD}" == "true" ] || DB_SERVER_ROOT_PASS=${DB_SERVER_ROOT_PASS:-${MYSQL_PASSWORD}}
    DB_SERVER_USER=${MYSQL_USER:-"labnda"}
    DB_SERVER_PASS=${MYSQL_PASSWORD:-"l4bnd4_"}
    DB_SERVER_DBNAME=${MYSQL_DATABASE:-"labndadb"}
}

configure_app(){
   CONFFILE="/usr/src/app/sigilaalarmas/config/config.yaml"
   sed -i 's/%DB_SERVER_HOST%/'"${DB_SERVER_HOST}"'/g' ${CONFFILE}
   sed -i 's/%MYSQL_USER%/'"${MYSQL_USER}"'/g' ${CONFFILE}
   sed -i 's/%MYSQL_PASSWORD%/'"${MYSQL_PASSWORD}"'/g' ${CONFFILE}
   sed -i 's/%MYSQL_DATABASE%/'"${MYSQL_DATABASE}"'/g' ${CONFFILE}
   #echo "FICHERO DE CONFIGURACION"
   #echo "------------------------"
   #cat $CONFFILE
}

# Check prerequisites for PostgreSQL database
check_variables_postgresql() {
    DB_SERVER_HOST=${DB_SERVER_HOST:-"postgres-server"}
    DB_SERVER_PORT=${DB_SERVER_PORT:-"5432"}
    CREATE_DB_USER=${CREATE_DB_USER:-"false"}

    DB_SERVER_ROOT_USER=${POSTGRES_USER:-"postgres"}
    DB_SERVER_ROOT_PASS=${POSTGRES_PASSWORD:-""}

    DB_SERVER_USER=${POSTGRES_USER:-"labnda"}
    DB_SERVER_PASS=${POSTGRES_PASSWORD:-"l4nbd4_"}
    DB_SERVER_DBNAME=${POSTGRES_DB:-"labndadb"}
}

check_db_connect_mysql() {
    echo "********************"
    echo "* DB_SERVER_HOST: ${DB_SERVER_HOST}"
    echo "* DB_SERVER_PORT: ${DB_SERVER_PORT}"
    echo "* DB_SERVER_DBNAME: ${DB_SERVER_DBNAME}"
    if [ "${USE_DB_ROOT_USER}" == "true" ]; then
        echo "* DB_SERVER_ROOT_USER: ${DB_SERVER_ROOT_USER}"
        echo "* DB_SERVER_ROOT_PASS: ${DB_SERVER_ROOT_PASS}"
    fi
    echo "* DB_SERVER_USER: ${DB_SERVER_USER}"
    echo "* DB_SERVER_PASS: ${DB_SERVER_PASS}"
    echo "********************"

    WAIT_TIMEOUT=5

    while [ ! "$(mysqladmin ping -h ${DB_SERVER_HOST} -P ${DB_SERVER_PORT} -u ${DB_SERVER_ROOT_USER} \
                --password="${DB_SERVER_ROOT_PASS}" --silent --connect_timeout=10)" ]; do
        echo "**** MySQL server is not available. Waiting $WAIT_TIMEOUT seconds..."
        sleep $WAIT_TIMEOUT
    done
}

check_db_connect_postgresql() {
    echo "********************"
    echo "* DB_SERVER_HOST: ${DB_SERVER_HOST}"
    echo "* DB_SERVER_PORT: ${DB_SERVER_PORT}"
    echo "* DB_SERVER_DBNAME: ${DB_SERVER_DBNAME}"
    if [ "${USE_DB_ROOT_USER}" == "true" ]; then
        echo "* DB_SERVER_ROOT_USER: ${DB_SERVER_ROOT_USER}"
        echo "* DB_SERVER_ROOT_PASS: ${DB_SERVER_ROOT_PASS}"
    fi
    echo "* DB_SERVER_USER: ${DB_SERVER_USER}"
    echo "* DB_SERVER_PASS: ${DB_SERVER_PASS}"
    echo "********************"

    if [ -n "${DB_SERVER_PASS}" ]; then
        export PGPASSWORD="${DB_SERVER_PASS}"
    fi

    WAIT_TIMEOUT=5

    while [ ! "$(psql -h ${DB_SERVER_HOST} -p ${DB_SERVER_PORT} -U ${DB_SERVER_ROOT_USER} -l -q 2>/dev/null)" ]; do
        echo "**** PostgreSQL server is not available. Waiting $WAIT_TIMEOUT seconds..."
        sleep $WAIT_TIMEOUT
    done

    unset PGPASSWORD
}


mysql_query() {
    query=$1
    local result=""

    result=$(mysql --silent --skip-column-names -h ${DB_SERVER_HOST} -P ${DB_SERVER_PORT} \
             -u ${DB_SERVER_ROOT_USER} --password="${DB_SERVER_ROOT_PASS}" -e "$query")

    echo $result
}

psql_query() {
    query=$1
    db=$2

    local result=""

    if [ -n "${DB_SERVER_PASS}" ]; then
        export PGPASSWORD="${DB_SERVER_PASS}"
    fi

    result=$(psql -A -q -t  -h ${DB_SERVER_HOST} -p ${DB_SERVER_PORT} \
             -U ${DB_SERVER_ROOT_USER} -c "$query" $db 2>/dev/null);

    unset PGPASSWORD

    echo $result
}

create_db_user_mysql() {
    [ "${CREATE_DB_USER}" == "true" ] || return

    echo "** Creating '${DB_SERVER_USER}' user in MySQL database"

    USER_EXISTS=$(mysql_query "SELECT 1 FROM mysql.user WHERE user = '${DB_SERVER_USER}' AND host = '%'")

    if [ -z "$USER_EXISTS" ]; then
        mysql_query "CREATE USER '${DB_SERVER_USER}'@'%' IDENTIFIED BY '${DB_SERVER_PASS}'" 1>/dev/null
    else
        mysql_query "SET PASSWORD FOR '${DB_SERVER_USER}'@'%' = PASSWORD('${DB_SERVER_PASS}');" 1>/dev/null
    fi

    mysql_query "GRANT ALL PRIVILEGES ON $DB_SERVER_DBNAME. * TO '${DB_SERVER_USER}'@'%'" 1>/dev/null
}

create_db_user_postgresql() {
    [ "${CREATE_DB_USER}" == "true" ] || return

    echo "** Creating '${DB_SERVER_USER}' user in PostgreSQL database"

    USER_EXISTS=$(psql_query "SELECT 1 FROM pg_roles WHERE rolname='${DB_SERVER_USER}'")

    if [ -z "$USER_EXISTS" ]; then
        psql_query "CREATE USER ${DB_SERVER_USER} WITH PASSWORD '${DB_SERVER_PASS}'" 1>/dev/null
    else
        psql_query "ALTER USER ${DB_SERVER_USER} WITH ENCRYPTED PASSWORD '${DB_SERVER_PASS}'" 1>/dev/null
    fi
}

create_db_database_mysql() {
    DB_EXISTS=$(mysql_query "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME='${DB_SERVER_DBNAME}'")

    if [ -z ${DB_EXISTS} ]; then
        echo "** Database '${DB_SERVER_DBNAME}' does not exist. Creating..."
        mysql_query "CREATE DATABASE ${DB_SERVER_DBNAME} CHARACTER SET utf8 COLLATE utf8_bin" 1>/dev/null
        # better solution?
        mysql_query "GRANT ALL PRIVILEGES ON $DB_SERVER_DBNAME. * TO '${DB_SERVER_USER}'@'%'" 1>/dev/null
    else
        echo "** Database '${DB_SERVER_DBNAME}' already exists. Please be careful with database COLLATE!"
    fi
}

create_db_database_postgresql() {
    DB_EXISTS=$(psql_query "SELECT 1 AS result FROM pg_database WHERE datname='${DB_SERVER_DBNAME}'")

    if [ -z ${DB_EXISTS} ]; then
        echo "** Database '${DB_SERVER_DBNAME}' does not exist. Creating..."
        psql_query "CREATE DATABASE ${DB_SERVER_DBNAME} WITH OWNER ${DB_SERVER_USER} ENCODING='UTF8' LC_CTYPE='en_US.utf8' LC_COLLATE='en_US.utf8'" 1>/dev/null
    else
        echo "** Database '${DB_SERVER_DBNAME}' already exists. Please be careful with database owner!"
    fi
}

create_db_schema_mysql() {
    DBVERSION_TABLE_EXISTS=$(mysql_query "SELECT 1 FROM information_schema.tables WHERE table_schema='${DB_SERVER_DBNAME}' and table_name = 'dbversion'")

    if [ -n "${DBVERSION_TABLE_EXISTS}" ]; then
        echo "** Table '${DB_SERVER_DBNAME}.dbversion' already exists."
        DB_VERSION=$(mysql_query "SELECT mandatory FROM ${DB_SERVER_DBNAME}.dbversion")
    fi

    if [ -z "${DB_VERSION}" ]; then
        echo "** Creating '${DB_SERVER_DBNAME}' schema in MySQL"

        cat /tmp/schema.sql | mysql --silent --skip-column-names \
                    -h ${DB_SERVER_HOST} -P ${DB_SERVER_PORT} \
                    -u ${DB_SERVER_ROOT_USER} --password="${DB_SERVER_ROOT_PASS}"  \
                    ${DB_SERVER_DBNAME} 1>/dev/null
    fi
}

create_db_schema_postgresql() {
    DBVERSION_TABLE_EXISTS=$(psql_query "SELECT 1 FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n ON n.oid =
                                         c.relnamespace WHERE  n.nspname = 'public' AND c.relname = 'dbversion'" "${DB_SERVER_DBNAME}")

    if [ -n "${DBVERSION_TABLE_EXISTS}" ]; then
        echo "** Table '${DB_SERVER_DBNAME}.dbversion' already exists."
        DB_VERSION=$(psql_query "SELECT mandatory FROM public.dbversion" "${DB_SERVER_DBNAME}")
    fi

    if [ -z "${DB_VERSION}" ]; then
        echo "** Creating '${DB_SERVER_DBNAME}' schema in PostgreSQL"

        if [ -n "${DB_SERVER_PASS}" ]; then
            export PGPASSWORD="${DB_SERVER_PASS}"
        fi

        cat /tmp/schema.sql | psql -q \
                -h ${DB_SERVER_HOST} -p ${DB_SERVER_PORT} \
                -U ${DB_SERVER_USER} ${DB_SERVER_DBNAME} 1>/dev/null
        unset PGPASSWORD
    fi
}

#Executing Fuctions
check_variables_mysql
check_db_connect_mysql
create_db_user_mysql
create_db_database_mysql
create_db_schema_mysql
configure_app


echo "########################################################"

#echo "** Executing supervisord"
#exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf

#echo "** Executing dockerize"
#exec dockerize -wait tcp://${DB_SERVER_HOST}:${DB_SERVER_PORT} -template /tmp/settings.tmpl:/usr/src/app/entorno/settings.py python /usr/src/app/manage.py runserver 0.0.0.0:8000

echo "Ejecutando servidor"
python run.py foreground
