#!/usr/bin/env bash

if [ "$MODE" == "deploy" ]; then
    gunicorn server:APP -b 0.0.0.0:2304 -w 4 -k uvicorn.workers.UvicornWorker
else
    uvicorn server:APP --host 0.0.0.0 --port 2304 --reload
fi
