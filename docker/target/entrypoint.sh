#!/bin/bash
set -e
if [ -n "$SCENARIO" ] && [ -f "/scenarios/$SCENARIO/setup.sh" ]; then
  echo "[seed] applying scenario: $SCENARIO"
  bash "/scenarios/$SCENARIO/setup.sh"
fi
exec "$@"