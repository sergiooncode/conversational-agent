#!/usr/bin/env bash

set -e

GREEN='\33[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

cd /opt/orbio

if [ "$1" = "yes" ]
then
    echo -e "${RED}Running${NC} black..."
    black src/
else
    echo -e "${GREEN}Running${NC} black..."
    black src/ --check

    echo -e "${GREEN}Running${NC} mypy..."
    cd /opt/orbio/src/
    mypy --config-file=../mypy.ini bff
fi