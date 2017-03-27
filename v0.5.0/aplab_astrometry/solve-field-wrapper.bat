@set /p CW_IN_PATH=< "%~dp0cygwin_install_path.txt"
@set /p ADN_IN_PATH=< "%~dp0astrometry\astrometry_install_path.txt"
@set ADN_BASE_PATH=%CW_IN_PATH%\home\%USERNAME%\astrometry
@set BASH=%CW_IN_PATH%\bin\bash

@xcopy /q /i /y "%~1\%~2" "%ADN_BASE_PATH%\solved_images\%~2\"

@"%BASH%" --login -c "%ADN_IN_PATH%/bin/solve-field %~3 ""$(cygpath -u -a '%ADN_BASE_PATH%\solved_images\%~2\%~2')"""

@move /y "%ADN_BASE_PATH%\solved_images\%~2" "%~dp0astrometry\solved_images\%~2"
