#!/bin/bash

ENV="/webapps/decaptcha"
PROJECT="$ENV/proj"
LOG="$PROJECT/log"
ADDRESS=${APP_ADDRESS-"0.0.0.0:8020"}
WORKER_CLS=${GUNICORN_WORKER_CLS-"sync"}

test -d $LOG || mkdir -p $LOG
source $ENV/.variables
exec $ENV/bin/gunicorn app:app \
    --worker-class $WORKER_CLS \
    --bind $ADDRESS \
    --config $PROJECT/conf/gunicorn_conf.py
