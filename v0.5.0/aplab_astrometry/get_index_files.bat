@set /p CW_IN_PATH=< "%~dp0cygwin_install_path.txt"
@set ADN_USR_PATH=%CW_IN_PATH%\home\%USERNAME%
@set ADN_BASE_PATH=%ADN_USR_PATH%\astrometry
@set BASH=%CW_IN_PATH%\bin\bash

@echo Running get_index_files.sh
"%BASH%" --login -c "cd astrometry/; ./get_index_files.sh %1 %2"

@echo Copying setup_log.txt to astrometry\
@copy /y "%ADN_BASE_PATH%\setup_log.txt" "%~dp0astrometry\"
