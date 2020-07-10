#!/bin/bash

envsubst < config.py.template > config.py
docker build -t $DOCKER_BUILD_TAG .
