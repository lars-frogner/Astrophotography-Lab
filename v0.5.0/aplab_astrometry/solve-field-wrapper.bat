@set /p CW_PATH_WIN=< "%~dp0cygwin_install_path.txt"
@set BASH=%CW_PATH_WIN%\bin\bash

@set /p ADN_WORK_PATH_CW=< "%~dp0astrometry_working_path.txt"
@set ADN_WORK_PATH_WIN=%CW_PATH_WIN%%ADN_WORK_PATH_CW:/=\%

@set ADN_PATH_CW=%ADN_WORK_PATH_CW%/astrometry
@set ADN_PATH_WIN=%ADN_WORK_PATH_WIN%\astrometry

@xcopy /q /i /y "%~1\%~2" "%ADN_PATH_WIN%\solved_images\%~2\"

@"%BASH%" --login -c """%ADN_PATH_CW%/solve-field-wrapper.sh"" ""$1"" ""$2"" ""$3""" "cygwin-wrapper" "" "%~2" "%~3"

@move /y "%ADN_PATH_WIN%\solved_images\%~2" "%~dp0astrometry\solved_images\%~2"
