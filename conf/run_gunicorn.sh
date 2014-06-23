#!/bin/bash

ENV="/webapps/decaptcha"
PROJECT="$ENV/proj"

exec $ENV/bin/gunicorn app:app \
    --config $PROJECT/conf/gunicorn_conf.py
