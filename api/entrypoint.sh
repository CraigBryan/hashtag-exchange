#!/bin/bash

if [ -z $ENVIRONMENT == "prod" ]; then
    yarn start-prod
else
    yarn start-dev
fi
