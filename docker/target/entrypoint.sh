#!/bin/bash
set -e

if [ -n "$SCENARIO" ] && [ -f "/root/scenarios/$SCENARIO/setup.sh" ]; then
  echo "[seed] applying scenario: $SCENARIO"
  bash "/root/scenarios/$SCENARIO/setup.sh"
fi

exec setpriv --reuid=target --regid=target --init-groups --reset-env "$@"