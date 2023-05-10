#!/usr/bin/env sh
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2023 DB Systel GmbH

TIMEOUT=600

echo "Starting container and waiting for command"
while true; do
    sleep $TIMEOUT
done

echo "Timeout of $TIMEOUT seconds reached. Stopping"
exit 60
