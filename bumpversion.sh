#!/bin/bash
. "$(dirname ${BASH_SOURCE:-$0})/config.inc"

# Read the version number from the file
version=$(grep 'IMAGE_VER' config.inc | cut -d '"' -f 2)

# Remove the 'v' prefix
version=${version#v}

# Split the version number by the delimiter '.'
major=$(echo $version | cut -d '.' -f 1)
minor=$(echo $version | cut -d '.' -f 2)
revision=$(echo $version | cut -d '.' -f 3)
build_sha=$(echo $version | cut -d '.' -f 4)

echo "Major: " $major
echo "Minor: " $minor
echo "Revision: " $revision
echo "Config Build Sha: " $build_sha

# Run flake8 against all code in the `source_code` directory
CURRENT_BUILD_SHA=$(find . -type f -name '*.wasm' | sort -d | xargs -I{} sha1sum add_time_metric.diff build.sh requirements.txt Dockerfile wasmscore.py {} | sha1sum | cut -c 1-7 | awk '{print $1}')
echo "Actual Build Sha: " $CURRENT_BUILD_SHA

# Update major version and build sha
if [[ $1 == "Major" || $1 == "major" ]]; then
  sed -i "s/\(IMAGE_VERSION=.*\.\)[0-9a-fA-F]\+/\1$CURRENT_BUILD_SHA/" config.inc
  awk -F'.' -v OFS='.' '/IMAGE_VERSION/ {split($1,a, "v"); a[1]++; $1= "IMAGE_VERSION=\"" "v" a[1];}1' config.inc >temp && mv temp config.inc
  awk -F'.' -v OFS='.' '/IMAGE_VERSION/ {$2=0; print} !/IMAGE_VERSION/ {print}' config.inc >temp && mv temp config.inc
  awk -F'.' -v OFS='.' '/IMAGE_VERSION/ {$3=0; print} !/IMAGE_VERSION/ {print}' config.inc >temp && mv temp config.inc

# Update minor version and build sha
elif [[ $1 == "Minor" || $1 == "minor" ]]; then
  sed -i "s/\(IMAGE_VERSION=.*\.\)[0-9a-fA-F]\+/\1$CURRENT_BUILD_SHA/" config.inc
  awk -F'.' -v OFS='.' '/IMAGE_VERSION/ {$2++; print} !/IMAGE_VERSION/ {print}' config.inc >temp && mv temp config.inc
  awk -F'.' -v OFS='.' '/IMAGE_VERSION/ {$3=0; print} !/IMAGE_VERSION/ {print}' config.inc >temp && mv temp config.inc

# Update patch version and build sha
elif [[ $1 == "Patch" || $1 == "patch" ]]; then
  sed -i "s/\(IMAGE_VERSION=.*\.\)[0-9a-fA-F]\+/\1$CURRENT_BUILD_SHA/" config.inc
  awk -F'.' -v OFS='.' '/IMAGE_VERSION/ {$3++; print} !/IMAGE_VERSION/ {print}' config.inc >temp && mv temp config.inc

# Only update the build sha
elif [[ $1 == "" ]]; then
  sed -i "s/\(IMAGE_VERSION=.*\.\)[0-9a-fA-F]\+/\1$CURRENT_BUILD_SHA/" config.inc

elif [[ $1 != "" ]]; then
  echo ""
  echo "Invalid argument"
fi

echo ""
echo "Final Version: " $(grep 'IMAGE_VER' config.inc | cut -d '"' -f 2)
