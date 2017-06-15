FROM python:2-alpine

#labels
ARG BUILD_DATE
ARG PROJECT_NAME
ARG VCS_REF
ARG VERSION
ARG PROJECT_URL
ARG LBLDESCRIPTION
ARG VENDOR="CGA"
ARG MAINTAINER="David Carrera del Castillo <dcarrera@andared.ced.junta-andalucia.es>"

LABEL org.label-schema.build-date=${BUILD_DATE} \
      org.label-schema.name=${PROJECT_NAME} \
      org.label-schema.description=${LBLDESCRIPTION} \
      org.label-schema.url=${PROJECT_URL} \
      org.label-schema.vcs-ref=${VCS_REF} \
      org.label-schema.vcs-url=${PROJECT_URL} \
      org.label-schema.vendor=$VENDOR \
      org.label-schema.version=${VERSION:-latest} \
      org.label-schema.schema-version="1.0" \
      maintainer=${MAINTAINER} \
      Version=${VERSION:-latest} \
      Name=${PROJECT_NAME}




WORKDIR /usr/src/app
COPY . .

RUN apk add --update musl-dev \
              gcc \
              mariadb-dev \
              mariadb-libs \
              mariadb-client \
              mariadb-client-libs \
              libcrypto1.0\
              openssl-dev \
              libssl1.0 \
    && pip install --no-cache-dir -r requirements.txt \
    && chmod +x entrypoint.sh \
    && touch /tmp/sigila-alarmas.log \
    && ln -sf /dev/stdout /tmp/sigila-alarmas.log \
    && mv hosts.sql /tmp/schema.sql

CMD ["./entrypoint.sh"]
