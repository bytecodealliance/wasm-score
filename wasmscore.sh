#!/bin/bash
cd sightglass
python3.8 ./wasmscore.py $@
cd - > /dev/null