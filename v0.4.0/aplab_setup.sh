#!/bin/bash

# Get path to Astrophotography Lab directory
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

# Create aplab.desktop file
cat > aplab.desktop << EOF
[Desktop Entry]
Version=0.4.0
Name=Astrophotography Lab
Comment=Astrophoto analysation software.
Exec=sh -c "cd ${SCRIPTPATH//\ /\\ }/ && ./APLab"
Icon=${SCRIPTPATH}/aplab_icon.png
Terminal=false
Type=Application
Categories=Utility;Application;
EOF

# Make aplab.desktop executable
chmod +x aplab.desktop