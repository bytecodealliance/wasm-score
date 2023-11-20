#!/bin/bash
. "$(dirname ${BASH_SOURCE:-$0})/config.inc"
IMAGE_NAME="wasmscore"
ARCH=$(uname -m | awk '{print tolower($0)}')
KERNEL=$(uname -s | awk '{print tolower($0)}')
echo "Building ${IMAGE_NAME} version ${IMAGE_VER} for $ARCH."

# Create Docker Image
docker build -t ${IMAGE_NAME} --build-arg ARCH=$(uname -m) .

docker tag ${IMAGE_NAME} ${IMAGE_NAME}_${ARCH}_${KERNEL}:latest
docker tag ${IMAGE_NAME} ${IMAGE_NAME}_${ARCH}_${KERNEL}:${IMAGE_VER}

echo ""
echo "The entry point is a wrapper to the python script 'wasmscore.py'."
echo ""
echo "To run from this local build use command (for a list of more options use --help):"
echo "> docker run -ti ${IMAGE_NAME} <options>"
echo ""
