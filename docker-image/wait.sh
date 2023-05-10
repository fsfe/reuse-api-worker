#!/usr/bin/env sh

TIMEOUT=600

echo "Starting container and waiting for command"
while true; do
    sleep $TIMEOUT
done

echo "Timeout of $TIMEOUT seconds reached. Stopping"
exit 60
