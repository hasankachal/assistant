#!/bin/sh

set -e 

poe_api ui -H "${HOST}" -p "${PORT}" -v "${INSTANCE}"