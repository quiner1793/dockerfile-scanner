#!/bin/sh
if [ -r /proc/1/root ]; then
    echo "Access to /proc/1/root is permitted."
else
    echo "Access to /proc/1/root is denied. Exiting."
    exit 1
fi

if [ -S /var/run/docker.sock ]; then
    echo "Docker socket is available."
else
    echo "Docker socket is not available. Exiting."
    exit 1
fi

exec python -u main.py "$@"