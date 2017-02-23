#!/bin/bash

cd /home/lars/Documents/Python/APLab
pyinstaller APLab.py
mv /home/lars/Documents/Python/APLab/dist/APLab "/home/lars/Documents/Python/APLab/dist/Astrophotography Lab"
mv "/home/lars/Documents/Python/APLab/dist/Astrophotography Lab" /home/lars/Documents/Python/APLab/
cp /home/lars/Documents/Python/APLab/cameradata.txt "/home/lars/Documents/Python/APLab/Astrophotography Lab/"
cp /home/lars/Documents/Python/APLab/telescopedata.txt "/home/lars/Documents/Python/APLab/Astrophotography Lab/"
cp /home/lars/Documents/Python/APLab/aplab_icon.png "/home/lars/Documents/Python/APLab/Astrophotography Lab/"
cp /home/lars/Documents/Python/APLab/sim_orig_image.png "/home/lars/Documents/Python/APLab/Astrophotography Lab/"
cp /home/lars/Documents/Python/APLab/aplab.desktop "/home/lars/Documents/Python/APLab/Astrophotography Lab/"
rm -r /home/lars/Documents/Python/APLab/build
rm -r /home/lars/Documents/Python/APLab/dist
rm /home/lars/Documents/Python/APLab/APLab.spec
cd "/home/lars/Documents/Python/APLab/Astrophotography Lab"
cp cameradata.txt cameradata_backup.txt
cp telescopedata.txt telescopedata_backup.txt
