#!/bin/bash

set -euxo pipefail

MODEL_URL="https://storage.googleapis.com/mobilenet_v2/checkpoints/mobilenet_v2_1.4_224.tgz"
MODEL_DIR="assets/"
MODEL_FILE="mobilenet_v2_1.4_224_frozen.pb"

mkdir -p assets

if [ ! -f $MODEL_DIR/$MODEL_FILE ]; then
	echo "Downloading model to $MODEL_DIR/$MODEL_FILE"
	if which wget >/dev/null ; then
	wget -qO- $MODEL_URL | tar xvz -C $MODEL_DIR
	elif which curl >/dev/null ; then
	curl -sL $MODEL_URL | tar xvz -C $MODEL_DIR
	else
	echo "Couldn't find wget or curl."
	echo "Please download manually from \"$MODEL_URL\" and save the file in $MODEL_DIR."
	fi
fi
