#!/bin/bash

# Get path to the directory this script resides in
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

ADN_IN_PATH=$(< astrometry/astrometry_install_path.txt)

rm -r -f "astrometry/solved_images/$2"
mkdir "astrometry/solved_images/$2"
mv "$1/$2" "astrometry/solved_images/$2/"
"${ADN_IN_PATH}/bin/solve-field" "$3" "${SCRIPTPATH}/astrometry/solved_images/$2/$2"
