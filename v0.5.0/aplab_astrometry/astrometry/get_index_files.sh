#!/bin/bash

# Make sure the script aborts if an error occurs
set -e
        
echo 'Usage: sudo ./get_index_files.sh <first index> [<last index>]'

# Get path to the directory this script resides in
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

# Redirect output to file
LOG=${SCRIPTPATH}/setup_log.txt
echo 'Standard output and errors will be written to setup_log.txt'
echo 'Standard errors will also be displayed on screen'

echo "Working directory is ${SCRIPTPATH}" | tee "${LOG}"

# Find which directory to store index files in
INDEXPATH=$(< "${SCRIPTPATH}/astrometry_install_path.txt")/data
echo "Storing index files in ${INDEXPATH}" | tee -a "${LOG}"

# Find which range of index files to download
I1=$1
if [ "$2" = "" ]
then
    if [ $1 -lt 0 ]
    then
        echo "Invalid index $1"
        exit
    elif [ $1 -gt 19 ]
    then
        echo "Invalid index $1"
        exit
    fi
    I2=$1
    echo "Retrieving index file ${I1}.." | tee -a "${LOG}"
else
    if [ $1 -lt 0 ]
    then
        echo "Invalid lower index $1"
        exit
    elif [ $2 -gt 19 ]
    then
        echo "Invalid upper index $2"
        exit
    elif [ $1 -gt $2 ]
    then
        echo "Lower index $1 cannot exceed upper index $2"
        exit
    fi
    I2=$2
    echo "Retrieving index files ${I1} through ${I2}.." | tee -a "${LOG}"
fi

# Code for checking download size
: <<'END'
TOTALSIZE=0

# Get total download size
for (( i=${I1}; i<=${I2}; i++ ))
do
    if [ $i -lt 5 ]
    then
        for j in {0..47}
        do
            INDEXNAME=index-42$(printf %02d $i)-$(printf %02d $j).fits
            if [ ! -f ${INDEXPATH}/${INDEXNAME} ]
            then
                SIZE=$(curl --head http://data.astrometry.net/4200/${INDEXNAME} 2>&1 | sed -ne "/Content-Length/{s/.*: //;p}" | tr -d "[:space:]")
                TOTALSIZE=$(( TOTALSIZE + SIZE ))
            fi
        done

    elif [ $i -lt 8 ]
    then
        for j in {0..11}
        do
            INDEXNAME=index-42$(printf %02d $i)-$(printf %02d $j).fits
            if [ ! -f ${INDEXPATH}/${INDEXNAME} ]
            then
                SIZE=$(curl --head http://data.astrometry.net/4200/${INDEXNAME} 2>&1 | sed -ne "/Content-Length/{s/.*: //;p}" | tr -d "[:space:]")
                TOTALSIZE=$(( TOTALSIZE + SIZE ))
            fi
        done
    else
        INDEXNAME=index-42$(printf %02d $i).fits
        if [ ! -f ${INDEXPATH}/${INDEXNAME} ]
        then
            SIZE=$(curl --head http://data.astrometry.net/4200/${INDEXNAME} 2>&1 | sed -ne "/Content-Length/{s/.*: //;p}" | tr -d "[:space:]")
            TOTALSIZE=$(( TOTALSIZE + SIZE ))
        fi
    fi
done

read -p "${TOTALSIZE} bytes will be downloaded. Continue? " -n 1 -r
echo
if [[ ! ${REPLY} =~ ^[Yy]$ ]]
then
    [[ "$0" = "${BASH_SOURCE}" ]] && exit 1 || return 1
fi
END

# Download index files
for (( i=${I1}; i<=${I2}; i++ ))
do
    if [ $i -lt 5 ]
    then
        for j in {0..47}
        do
            INDEXNAME=index-42$(printf %02d $i)-$(printf %02d $j).fits
            if [ -f "${INDEXPATH}/${INDEXNAME}" ]
            then
                echo "${INDEXNAME} already exists" | tee -a "${LOG}"
            else
                echo "Downloading ${INDEXNAME}.." | tee -a "${LOG}"
                wget -P "${INDEXPATH}/" -O "${INDEXPATH}/${INDEXNAME}" "http://data.astrometry.net/4200/${INDEXNAME}" | tee -a "${LOG}"
            fi
        done

    elif [ $i -lt 8 ]
    then
        for j in {0..11}
        do
            INDEXNAME=index-42$(printf %02d $i)-$(printf %02d $j).fits
            if [ -f "${INDEXPATH}/${INDEXNAME}" ]
            then
                echo "${INDEXNAME} already exists" | tee -a "${LOG}"
            else
                echo "Downloading ${INDEXNAME}.." | tee -a "${LOG}"
                wget -P "${INDEXPATH}/" -O "${INDEXPATH}/${INDEXNAME}" "http://data.astrometry.net/4200/${INDEXNAME}" | tee -a "${LOG}"
            fi
        done
    else
        INDEXNAME=index-42$(printf %02d $i).fits
        if [ -f "${INDEXPATH}/${INDEXNAME}" ]
        then
            echo "${INDEXNAME} already exists" | tee -a "${LOG}"
        else
            echo "Downloading ${INDEXNAME}.." | tee -a "${LOG}"
            wget -P "${INDEXPATH}/" -O "${INDEXPATH}/${INDEXNAME}" "http://data.astrometry.net/4200/${INDEXNAME}" | tee -a "${LOG}"
        fi
    fi
done

echo 'Done' | tee -a "${LOG}"
