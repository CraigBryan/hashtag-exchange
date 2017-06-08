FROM node:boron

RUN apt-get update
RUN apt-get install apt-transport-https

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg |  apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

RUN apt-get update
RUN apt-get install yarn

COPY ./package.json ./package.json
COPY ./ensure_indices.js ./ensure_indices.js

RUN yarn install
ENTRYPOINT yarn ensure-indices 
