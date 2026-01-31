#!/bin/bash
echo "== Source file to be parsed $1"
echo "== AST file to be created $2"
echo "== Pre-Processor args $3"
SCRIPT_DIR=$(dirname "$0")
cd $SCRIPT_DIR
source toolbox/.venv/bin/activate
python toolbox/parse.py $1 $2 
# --cpp_args $3
