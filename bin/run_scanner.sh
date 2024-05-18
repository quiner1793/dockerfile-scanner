#!/bin/bash

DIR="./.venv"

if [ -d "$DIR" ]; then
  echo "venv exists"
else
  python3 -m venv ${DIR}
fi

source ${DIR}/bin/activate
pip install -r src/requirements.txt

cd src/ || exit 1
../${DIR}/bin/python3 main.py ../
