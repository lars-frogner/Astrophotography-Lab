#!/bin/bash

# Usage: ./solve-field-wrapper.sh <image path> <image name> <solve-field flags>

set -e

FILEPATH=${1//\"/}
FILENAME=${2//\"/}
BASENAME=${FILENAME%.*}
FLAGS=$3

# Detect platform
PLATFORM=$(uname -o)

# Get path to the directory this script resides in
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

# Get astrometry.net install path
ADN_IN_PATH=$(< ${SCRIPTPATH}/astrometry_install_path.txt)

# If on Linux, move image into solved_images folder
if [ ! "${PLATFORM}" = "Cygwin" ]
then
	rm -r -f "${SCRIPTPATH}/solved_images/${FILENAME}"
	mkdir "${SCRIPTPATH}/solved_images/${FILENAME}"
	mv "${FILEPATH}/${FILENAME}" "${SCRIPTPATH}/solved_images/${FILENAME}/"
fi

# Run solve-field command
"${ADN_IN_PATH}/bin/solve-field" ${FLAGS} "${SCRIPTPATH}/solved_images/${FILENAME}/${FILENAME}"

"${ADN_IN_PATH}/bin/wcsinfo" "${SCRIPTPATH}/solved_images/${FILENAME}/${BASENAME}.wcs" > "${BASENAME}_wcsinfo.txt"
