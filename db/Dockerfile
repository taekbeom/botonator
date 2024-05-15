FROM postgres:15

USER root

RUN mkdir -p /oracle/pg_data/archive/

RUN chmod -R 777 /oracle/pg_data/archive/

COPY init.sql /docker-entrypoint-initdb.d/

CMD ["postgres"]
