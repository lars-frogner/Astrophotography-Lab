@set /p CW_IN_PATH=< "%~dp0cygwin_install_path.txt"
@set ADN_USR_PATH=%CW_IN_PATH%\home\%USERNAME%
@set ADN_BASE_PATH=%ADN_USR_PATH%\astrometry
@set BASH=%CW_IN_PATH%\bin\bash

@echo Copying astrometry directory to %ADN_USR_PATH%\
@xcopy /s /e /h /i /y "astrometry" "%ADN_BASE_PATH%"

@echo Running astrometry_setup.sh
@"%BASH%" --login -c "cd astrometry/; ./astrometry_setup.sh %1"

@echo Copying setup_log.txt to astrometry\
@copy /y "%ADN_BASE_PATH%\setup_log.txt" "%~dp0astrometry\"

@echo Copying astrometry_install_path.txt to astrometry\
@copy /y "%ADN_BASE_PATH%\astrometry_install_path.txt" "%~dp0astrometry\"
