FROM python:2-alpine

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
