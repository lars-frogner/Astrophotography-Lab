#!/bin/bash
set -e
set -x

BASE='/home/lars/Dropbox/Programmering/Astrophotography/Astrophotography Lab [lrep]/v0.4.1'
TARFOLDER=aplab-v0.4.2-linux-64-bit-update
README=README_v0.4.2_linux.txt
NAME=APLab

cd "${BASE}"

echo 'Creating main executable...'
pyinstaller aplab_runner.py --name=$NAME

echo 'Organizing files...'

mv "${BASE}/dist/${NAME}/${NAME}" "${BASE}/"
rm -r "${BASE}/build"
rm -r "${BASE}/dist"
rm "${BASE}/${NAME}.spec"
rm "${BASE}/__pycache__/aplab_runner.cpython-35.pyc"

echo 'Compressing archive...'

cp "${BASE}/${README}" "${BASE}/README.txt"
tar -czf "${TARFOLDER}.tar.gz" -C "${BASE}" "${NAME}" README.txt
rm "${BASE}/${NAME}"
rm "${BASE}/README.txt"

echo Done
