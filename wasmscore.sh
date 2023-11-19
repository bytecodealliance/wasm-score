#!/bin/bash
cd sightglass
python3.10 ./wasmscore.py $@
cd - > /dev/null