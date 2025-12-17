FROM postgres:alpine
COPY ./init.sql /docker-entrypoint-initdb.d/
ENV POSTGRES_PASSWORD="postgres"
ENV POSTGRES_USER="postgres"
EXPOSE 5432

