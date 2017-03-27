@set /p CW_IN_PATH=< cygwin_install_path.txt
@set /p ADN_IN_PATH=< astrometry\astrometry_install_path.txt
@set ADN_BASE_PATH=%CW_IN_PATH%\home\%USERNAME%\astrometry
@set BASH=%CW_IN_PATH%\bin\bash

@echo Getting required index file
@call get_index_files.bat 11

@echo Solving apod2.jpg
@"%BASH%" --login -c "cd astrometry/; %ADN_IN_PATH%/bin/solve-field --scale-low 1 astrometry.net-*/demo/apod2.jpg; cp astrometry.net-*/demo/apod2-ngc.png ""$(cygpath -u -a '%~dp0')"""

@echo Solved image in apod2-ngc.png
