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
echo "To run from this local build use command:"
echo "> docker run -ti ${IMAGE_NAME} /bin/bash wasmscore.sh --help"
echo ""
echo "To stop and rm all ${IMAGE_NAME} containers:"
echo "> docker rm \$(docker stop \$(docker ps -a -q --filter ancestor=${IMAGE_NAME}:latest --format="{{.ID}}"))"
echo ""
echo "For a detached setup that allows for copying files to the image or"
echo "entering the container, use the following commands:"
echo "> docker run -ti -d ${IMAGE_NAME} /bin/bash"
echo "> wasmscore_container_id=\$(docker ps | grep -m 1 ${IMAGE_NAME} | awk '{ print \$1 }')"
echo "> docker cp <file> \${wasmscore_container_id}:"
echo "or"
echo "> docker exec -ti \${wasmscore_container_id} /bin/bash"
echo ""
