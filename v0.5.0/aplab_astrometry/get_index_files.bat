@set /p CW_PATH_WIN=< "%~dp0cygwin_install_path.txt"
@set BASH=%CW_PATH_WIN%\bin\bash

@set /p ADN_WORK_PATH_CW=< "%~dp0astrometry_working_path.txt"
@set ADN_WORK_PATH_WIN=%CW_PATH_WIN%%ADN_WORK_PATH_CW:/=\%

@set ADN_PATH_CW=%ADN_WORK_PATH_CW%/astrometry
@set ADN_PATH_WIN=%ADN_WORK_PATH_WIN%\astrometry

@echo Running get_index_files.sh
@"%BASH%" --login -c """%ADN_PATH_CW%/get_index_files.sh"" %~1 %~2" "cygwin-wrapper"

@echo Copying setup_log.txt to astrometry\
@copy /y "%ADN_PATH_WIN%\setup_log.txt" "%~dp0astrometry\"
