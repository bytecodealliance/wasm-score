#!/bin/bash

# Read the version number from the file
IMAGE_NAME=$(grep 'IMAGE_NAME' config.inc | cut -d '"' -f 2)
IMAGE_VERSION=$(grep 'IMAGE_VERSION' config.inc | cut -d '"' -f 2)
VERSION=${IMAGE_VERSION#v}

# Split the version number by the delimiter '.'
MAJOR=$(echo $VERSION | cut -d '.' -f 1)
MINOR=$(echo $VERSION | cut -d '.' -f 2)
REVISION=$(echo $VERSION | cut -d '.' -f 3)
BUILD_SHA=$(echo $VERSION | cut -d '.' -f 4)

# Define current build and commit SHAs
# Sort -n/-h produced different sort results for inside vs outside the countainer so using sort -d
CURRENT_BUILD_SHA=$(find . -type f -name '*.wasm' | sort -d | xargs -I{} sha1sum add_time_metric.diff build.sh requirements.txt Dockerfile wasmscore.py {} | sha1sum | cut -c 1-7 | awk '{print $1}')

# Define architecutre and kernel
ARCH=$(uname -m | awk '{print tolower($0)}')
KERNEL=$(uname -s | awk '{print tolower($0)}')

# Print build information
echo ""
echo "Build information"
echo "-----------------"
echo "Major:" $MAJOR
echo "Minor:" $MINOR
echo "Revision:" $REVISION
echo "Build Sha:" $BUILD_SHA "vs" $CURRENT_BUILD_SHA "(calculated)"
echo ""


# Create docker image
echo "Building ${IMAGE_NAME}-${IMAGE_VERSION} for $ARCH."
echo ""
docker build -t ${IMAGE_NAME} --build-arg ARCH=$(uname -m) .
docker tag ${IMAGE_NAME} ${IMAGE_NAME}_${ARCH}_${KERNEL}:latest
docker tag ${IMAGE_NAME} ${IMAGE_NAME}_${ARCH}_${KERNEL}:${IMAGE_VERSION}

# Print instructions
echo ""
echo "The entry point is a wrapper to the python script 'wasmscore.py'"
echo "To run from this local build use command (for a list of more options use --help):"
echo "> docker run -ti ${IMAGE_NAME} <options>"
echo ""
echo "To stop and rm all ${IMAGE_NAME} containers:"
echo "> docker rm \$(docker stop \$(docker ps -a -q --filter ancestor=${IMAGE_NAME}:latest --format="{{.ID}}"))"
echo ""
echo "For a detached setup that allows for copying files to the image or"
echo "entering the container, use the following commands:"
echo "> docker run --entrypoint=/bin/bash -ti -d ${IMAGE_NAME}"
echo "> wasmscore_container_id=\$(docker ps | grep -m 1 ${IMAGE_NAME} | awk '{ print \$1 }')"
echo ""
echo "> docker cp <file> \${wasmscore_container_id}:"
echo "or"
echo "> docker exec -ti \${wasmscore_container_id}" /bin/bash
echo ""
