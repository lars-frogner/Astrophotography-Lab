@set /p CW_PATH_WIN=< "%~dp0cygwin_install_path.txt"
@set BASH=%CW_PATH_WIN%\bin\bash

@set /p ADN_WORK_PATH_CW=< "%~dp0astrometry_working_path.txt"
@set ADN_WORK_PATH_WIN=%CW_PATH_WIN%%ADN_WORK_PATH_CW:/=\%

@set ADN_PATH_CW=%ADN_WORK_PATH_CW%/astrometry
@set ADN_PATH_WIN=%ADN_WORK_PATH_WIN%\astrometry

@echo Copying astrometry directory to %ADN_WORK_PATH_WIN%\
@xcopy /s /e /h /i /y "astrometry" "%ADN_PATH_WIN%"

@echo Running astrometry_setup.sh
@"%BASH%" --login -c """%ADN_PATH_CW%/astrometry_setup.sh"" ""$1""" "cygwin-wrapper" "%~1"

@echo Copying setup_log.txt to astrometry\
@copy /y "%ADN_PATH_WIN%\setup_log.txt" "%~dp0astrometry\"
