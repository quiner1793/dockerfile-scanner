#!/bin/bash

DIR="./.venv"

if [ -d "$DIR" ]; then
  echo "venv exists"
else
  python3 -m venv ${DIR}
fi

# Checking if the permissions need to be modified
if [ ! -w "$DIR" ]; then
  echo "venv is not writable. Attempting to change permissions."
  chmod -R u+w "$DIR"

  # Verifying if chmod succeeded
  if [ $? -ne 0 ]; then
    echo "Failed to change permissions for $DIR"
    exit 1
  else
    echo "Permissions changed successfully for $DIR"
  fi
fi

source ${DIR}/bin/activate
pip install -r src/requirements.txt

cd src/ || exit 1
../${DIR}/bin/python3 main.py "$1"
