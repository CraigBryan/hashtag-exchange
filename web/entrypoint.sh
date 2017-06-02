#!/bin/bash

if [ -z $ENVIRONMENT == "prod" ]; then
    yarn build-prod
else
    yarn build-dev
fi
