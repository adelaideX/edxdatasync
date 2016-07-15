#!/bin/bash

VIRTUALENV_INSTALLED=`which virtualenv`
if [ "$VIRTUALENV_INSTALLED" == "" ]; then
    echo -e "virtualenv NOT found."
    exit 1
fi

virtualenv --no-site-packages env
source env/bin/activate
pip install -r requirements.txt

export PYTHONPATH=.:$PYTHONPATH
echo "Run \"source env/bin/activate\" to activate this virtualenv."
