#!/bin/bash

DIR=$( cd ${0%/*} && pwd -P )
TODAY="$(date +'%Y%m%d')"

function log
{
    echo "[$(date +'%Y-%m-%d %H:%M:%S,%3N')][server/start.sh]: $1"
}

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -p|--sudo-pass) sudo_pass="$2"; shift ;;
	*) log "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [[ ! "$sudo_pass" ]]; then
    log "No sudo_pass specified"
    exit 1
fi

# Set the sudo pass environment variable
export SUDO_PASS=$sudo_pass

command="$DIR/main.py"
pid="$DIR/server.pid"

if test -f "$pid"; then
    log "PI Utility Server is already running.  Exiting..."
    exit 1
fi

((${command}) &>> $DIR/../logs/$TODAY.server.log & jobs -p > ${pid})
