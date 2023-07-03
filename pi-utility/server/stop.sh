#!/bin/bash

DIR=$( cd ${0%/*} && pwd -P )
TODAY="$(date +'%Y%m%d')"

function log
{
    echo "[$(date +'%Y-%m-%d %H:%M:%S,%3N')][server/stop.sh]: $1"
}

pid_file="$DIR/server.pid"

if ! test -f "$pid_file"; then
    log "$pid_file" does NOT exist. Exiting...
    exit 1
fi

pid="$(cat $pid_file)"

result="$(ps aux | grep $pid | grep -v grep | tr -s ' ' | cut -d ' ' -f11-)"

if [[ $result == *"$DIR/main.py"* ]]; then
    kill -SIGINT $pid
fi

rm $pid_file
