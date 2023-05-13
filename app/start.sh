#!/bin/bash
app="whitelist.discordbot"
docker build -t ${app} .
docker run -d \
    --name=${app} \
    -v $PWD:/app ${app}