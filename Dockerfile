FROM mongo

COPY ./mongodb-conf.yaml /etc/mongodb-conf.yaml
ENTRYPOINT mongod -f /etc/mongodb-conf.yaml

