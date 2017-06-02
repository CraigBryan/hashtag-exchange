FROM node:boron

RUN apt-get update
RUN apt-get install apt-transport-https

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg |  apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

RUN apt-get update
RUN apt-get install yarn

COPY api/entrypoint.sh /api/entrypoint.sh
COPY api/package.json /api/package.json

WORKDIR /api
RUN yarn install