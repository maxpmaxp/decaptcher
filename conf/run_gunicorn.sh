#!/bin/bash

ENV="/webapps/decaptcha"
PROJECT="$ENV/proj"
LOG="$PROJECT/log"
ADDRESS=${APP_ADDRESS-"0.0.0.0:8020"}

test -d $LOG || mkdir -p $LOG
source $ENV/.variables
exec $ENV/bin/gunicorn app:app \
    --bind $ADDRESS \
    --config $PROJECT/conf/gunicorn_conf.py
