#!/bin/bash
set -e
set -x

BASE='/home/lars/Dropbox/Programmering/Astrophotography/Astrophotography Lab [lrep]/v0.4.0'
FOLDER='Astrophotography Lab'
TARFOLDER=aplab-v0.4.0-linux-standalone
README=README_v0.4.0_linux.txt
NAME=APLab

cd "${BASE}"

echo Creating main executable...
python3 /home/lars/Downloads/pyinstaller-develop/pyinstaller.py aplab_runner.py --name=$NAME

echo Organizing files...

mv "${BASE}/dist/${NAME}" "${BASE}/dist/${FOLDER}"
mv "${BASE}/dist/${FOLDER}" "${BASE}/"
mkdir "${BASE}/${FOLDER}/aplab_temp"
mkdir "${BASE}/${FOLDER}/aplab_errorlog"
cp -R "${BASE}/aplab_data" "${BASE}/${FOLDER}/"
cp "${BASE}/aplab_icon.png" "${BASE}/${FOLDER}/"
cp "${BASE}/aplab_setup.sh" "${BASE}/${FOLDER}/"
rm -r "${BASE}/build"
rm -r "${BASE}/dist"
rm "${BASE}/${NAME}.spec"
rm "${BASE}/__pycache__/aplab_runner.cpython-35.pyc"
rm -r "${BASE}/${FOLDER}/share/icons"
cd "${BASE}/${FOLDER}/aplab_data"
cp cameradata.txt cameradata_backup.txt
cp telescopedata.txt telescopedata_backup.txt
cp objectdata.txt objectdata_backup.txt

echo Preparing zip package

cp "${BASE}/${README}" "${BASE}/README.txt"

echo Done
