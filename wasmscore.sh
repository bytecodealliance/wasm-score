#!/bin/bash
cd sightglass
python3 ./wasmscore.py $@
cd - > /dev/null