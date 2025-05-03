#!/usr/bin/env bash

set -e

GREEN='\33[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m' # No Color

ARG1=${1:-all}
ARG2=${2:-}

if [ "$ARG1" = "all" ]
then
  if [ "$ARG2" != "" ]
  then
      echo -e "${NC}Running${RED} ONLY ${NC}tests matching ${BOLD}'$1'..."
      pytest -sk $1 /opt/orbio/src/tests
  else
      echo -e "${NC}Running${GREEN} ALL ${NC}tests..."
      pytest /opt/orbio/src/tests
  fi

elif [ "$ARG1" = "from-path" ]
then
    echo -e "${NC}Running${RED} ONLY ${NC}tests matching relative path ${BOLD}'$2'..."
    pytest --continue-on-collection-errors /opt/orbio/$2

fi