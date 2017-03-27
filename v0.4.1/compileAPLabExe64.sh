#!/bin/bash
set -e
set -x

BASE='/home/lars/Dropbox/Programmering/Astrophotography/Astrophotography Lab [lrep]/v0.4.1'
FOLDER='Astrophotography Lab'
TARFOLDER=aplab-v0.4.1-linux-64-bit-standalone
README=README_v0.4.1_linux.txt
NAME=APLab

cd "${BASE}"

echo 'Creating main executable...'
pyinstaller aplab_runner.py --name=$NAME

echo 'Organizing files...'

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
cd "${BASE}"

echo 'Compressing archive...'

cp "${BASE}/${README}" "${BASE}/README.txt"
tar -czf "${TARFOLDER}.tar.gz" -C "${BASE}" "${FOLDER}" README.txt
rm -r "${BASE}/${FOLDER}"
rm "${BASE}/README.txt"

echo Done
