@set BASE=C:\Users\Lars\Dropbox\Programmering\Astrophotography\"Astrophotography Lab [lrep]"\v0.4.1
@set FOLDER="Astrophotography Lab"
@set ZIPFOLDER="aplab-v0.4.1-win-standalone"
@set README="README_v0.4.1_win.txt"
@set NAME=APLab

cd %BASE%
@if %errorlevel% neq 0 exit /b %errorlevel%

@echo Creating main executable...

pyinstaller aplab_runner.py --icon=aplab_icon.ico --name=%NAME% --noconsole
@if %errorlevel% neq 0 exit /b %errorlevel%

@echo Organizing files...

rename %BASE%\dist\%NAME% %FOLDER%
@if %errorlevel% neq 0 exit /b %errorlevel%

move %BASE%\dist\%FOLDER% %BASE%\%FOLDER%
@if %errorlevel% neq 0 exit /b %errorlevel%

mkdir %BASE%\%FOLDER%\aplab_temp
@if %errorlevel% neq 0 exit /b %errorlevel%

mkdir %BASE%\%FOLDER%\aplab_errorlog
@if %errorlevel% neq 0 exit /b %errorlevel%

xcopy %BASE%\aplab_data %BASE%\%FOLDER%\aplab_data /s /e /h /i
@if %errorlevel% neq 0 exit /b %errorlevel%

copy %BASE%\aplab_icon.ico %BASE%\%FOLDER%
@if %errorlevel% neq 0 exit /b %errorlevel%

copy %BASE%\dcraw.exe %BASE%\%FOLDER%
@if %errorlevel% neq 0 exit /b %errorlevel%

rmdir /S /Q %BASE%\build
@if %errorlevel% neq 0 exit /b %errorlevel%

rmdir /S /Q %BASE%\dist
@if %errorlevel% neq 0 exit /b %errorlevel%

del /Q %BASE%\%NAME%.spec
@if %errorlevel% neq 0 exit /b %errorlevel%

cd %BASE%\%FOLDER%\aplab_data
@if %errorlevel% neq 0 exit /b %errorlevel%

copy cameradata.txt cameradata_backup.txt
@if %errorlevel% neq 0 exit /b %errorlevel%

copy telescopedata.txt telescopedata_backup.txt
@if %errorlevel% neq 0 exit /b %errorlevel%

copy objectdata.txt objectdata_backup.txt
@if %errorlevel% neq 0 exit /b %errorlevel%

cd %BASE%

@echo Creating debug executable...

pyinstaller aplab_runner.py --icon=aplab_icon.ico --name=%NAME%_debug
@if %errorlevel% neq 0 exit /b %errorlevel%

@echo Organizing files...

move %BASE%\dist\%NAME%_debug\%NAME%_debug.exe %BASE%\%FOLDER%
@if %errorlevel% neq 0 exit /b %errorlevel%

move %BASE%\dist\%NAME%_debug\%NAME%_debug.exe.manifest %BASE%\%FOLDER%
@if %errorlevel% neq 0 exit /b %errorlevel%

rmdir /S /Q %BASE%\build
@if %errorlevel% neq 0 exit /b %errorlevel%

rmdir /S /Q %BASE%\dist
@if %errorlevel% neq 0 exit /b %errorlevel%

del /Q %BASE%\%NAME%_debug.spec
@if %errorlevel% neq 0 exit /b %errorlevel%

del /Q %BASE%\__pycache__\"aplab_runner.cpython-35.pyc"
@if %errorlevel% neq 0 exit /b %errorlevel%

@echo Preparing zip package

copy %BASE%\%README% %BASE%\README.txt
@if %errorlevel% neq 0 exit /b %errorlevel%

@echo Compressing archive...

@7z a -mx9 -tzip %ZIPFOLDER%.zip %FOLDER%\ README.txt
@rmdir /S /Q %FOLDER%
@del /Q README.txt

@echo Done