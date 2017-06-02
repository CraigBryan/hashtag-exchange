FROM node:boron

RUN apt-get update && apt-get install apt-transport-https

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg |  apt-key add -
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list

RUN apt-get update && apt-get install yarn

RUN yarn install

COPY entrypoint.sh ./entrypoint.sh
COPY package.json ./package.json
COPY .babelrc ./.babelrc
