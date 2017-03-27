#!/bin/bash

# This variable must equal the path to the netpbm library
NETPBM_LIB_PATH=/usr/lib

# This variable must equal the path to the netpbm header
NETPBM_HEAD_PATH=/usr/include

# Make sure the script aborts if an error occurs
set -e

echo 'Usage: ./astrometry_setup.sh [</path/to/install/to>]'

# Get path to the directory this script resides in
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

# Redirect output to files
LOG=${SCRIPTPATH}/setup_log.txt
echo 'Standard output and errors will be written to setup_log.txt'
echo 'Standard errors will also be displayed on screen'

# Detect platform
PLATFORM=$(uname -o)
echo "Platform is ${PLATFORM}" | tee ${LOG}

echo "Working directory is ${SCRIPTPATH}" | tee -a ${LOG}

# Set installation path
if [ "$1" = "" ]
then
    INSTALLPATH='/usr/local/astrometry'
else
    INSTALLPATH=$1
    export INSTALL_DIR=${INSTALLPATH}
fi
echo "Installation path is ${INSTALLPATH}" | tee -a ${LOG}
echo "${INSTALLPATH}" > astrometry_install_path.txt

# Make sure dependencies are installed
if [ "${PLATFORM}" = "Cygwin" ]
then
	echo 'Installing pyfits..' | tee -a ${LOG}
	easy_install-2.7 pyfits 2>&1 >> ${LOG} | tee -a ${LOG}
else
	echo 'Installing libcairo2-dev..' | tee -a ${LOG}
	apt-get install libcairo2-dev 2>&1 >> ${LOG} | tee -a ${LOG}
	echo 'Installing libnetpbm10-dev..' | tee -a ${LOG}
	apt-get install libnetpbm10-dev 2>&1 >> ${LOG} | tee -a ${LOG}
	echo 'Installing netpbm..' | tee -a ${LOG}
	apt-get install netpbm 2>&1 >> ${LOG} | tee -a ${LOG}
	echo 'Installing libpng12-dev..' | tee -a ${LOG}
	apt-get install libpng12-dev 2>&1 >> ${LOG} | tee -a ${LOG}
	echo 'Installing libjpeg-dev..' | tee -a ${LOG}
	apt-get install libjpeg-dev 2>&1 >> ${LOG} | tee -a ${LOG}
	echo 'Installing python-numpy..' | tee -a ${LOG}
	apt-get install python-numpy 2>&1 >> ${LOG} | tee -a ${LOG}
	echo 'Installing python-pyfits..' | tee -a ${LOG}
	apt-get install python-pyfits 2>&1 >> ${LOG} | tee -a ${LOG}
	echo 'Installing python-dev..' | tee -a ${LOG}
	apt-get install python-dev 2>&1 >> ${LOG} | tee -a ${LOG}
	echo 'Installing zlib1g-dev..' | tee -a ${LOG}
	apt-get install zlib1g-dev 2>&1 >> ${LOG} | tee -a ${LOG}
	echo 'Installing libbz2-dev..' | tee -a ${LOG}
	apt-get install libbz2-dev 2>&1 >> ${LOG} | tee -a ${LOG}
	echo 'Installing swig..' | tee -a ${LOG}
	apt-get install swig 2>&1 >> ${LOG} | tee -a ${LOG}
fi

# Retrieve and unpack CFITSIO source
if [ ! -d cfitsio ]
then
	if [ ! -f cfitsio_latest.tar.gz ]
	then
		echo "Downloading cfitsio_latest.tar.gz.." | tee -a ${LOG}
		wget -O cfitsio_latest.tar.gz http://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/cfitsio_latest.tar.gz | tee -a ${LOG}
	else
		echo 'cfitsio_latest.tar.gz already exists'
	fi
	echo 'Unpacking cfitsio_latest.tar.gz..' | tee -a ${LOG}
	tar xf cfitsio_latest.tar.gz 2>&1 >> ${LOG} | tee -a ${LOG}
	rm -f cfitsio_latest.tar.gz 2>&1 >> ${LOG} | tee -a ${LOG}
else
	echo 'cfitsio/ already exists'
fi

# Retrieve and unpack astrometry.net source
if [ ! -d astrometry.net-* ]
then
	if [ ! -f astrometry.net-latest.tar.gz ]
	then
		echo "Downloading astrometry.net-latest.tar.gz.." | tee -a ${LOG}
		wget -O astrometry.net-latest.tar.gz http://astrometry.net/downloads/astrometry.net-latest.tar.gz | tee -a ${LOG}
	else
		echo 'astrometry.net-latest.tar.gz already exists'
	fi
	echo 'Unpacking astrometry.net-latest.tar.gz..' | tee -a ${LOG}
	tar xf astrometry.net-latest.tar.gz 2>&1 >> ${LOG} | tee -a ${LOG}
	rm -f astrometry.net-latest.tar.gz 2>&1 >> ${LOG} | tee -a ${LOG}
else
	echo "astrometry.net-*/ already exists"
fi

echo 'Attention! Error messages may follow. Ignore them unless the script stops'

# Build CFITSIO
cd cfitsio/
echo 'Running CFITSIO configure..' | tee -a ${LOG}
./configure 2>&1 >> ${LOG} | tee -a ${LOG}
echo 'Running CFITSIO make..' | tee -a ${LOG}
make 2>&1 >> ${LOG} | tee -a ${LOG}
echo 'Running CFITSIO make install..' | tee -a ${LOG}
make install 2>&1 >> ${LOG} | tee -a ${LOG}
cd ..

# Build astrometry.net
echo 'Setting environment variables..'
export CFITS_INC="-I${SCRIPTPATH}/cfitsio/include"
export CFITS_LIB="-L${SCRIPTPATH}/cfitsio/lib -lcfitsio"
export NETPBM_LIB="-L${NETPBM_LIB_PATH} -lnetpbm"
export NETPBM_INC="-I${NETPBM_HEAD_PATH}/netpbm -I${NETPBM_HEAD_PATH}"

cd astrometry.net-*/
echo 'Running astrometry.net make..' | tee -a ${LOG}
make 2>&1 >> ${LOG} | tee -a ${LOG}
echo 'Running astrometry.net make py..' | tee -a ${LOG}
make py 2>&1 >> ${LOG} | tee -a ${LOG}
echo 'Running astrometry.net make extra..' | tee -a ${LOG}
make extra 2>&1 >> ${LOG} | tee -a ${LOG}
echo 'Running astrometry.net make install..' | tee -a ${LOG}
make install 2>&1 >> ${LOG} | tee -a ${LOG}
cd ..

echo 'Done' | tee -a ${LOG}
