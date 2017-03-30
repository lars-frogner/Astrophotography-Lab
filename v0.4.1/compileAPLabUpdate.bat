@set BASE=C:\Users\Lars\Dropbox\Programmering\Astrophotography\"Astrophotography Lab [lrep]"\v0.4.1
@set ZIPFOLDER="aplab-v0.4.2-win-update"
@set README="README_v0.4.2_win.txt"
@set NAME=APLab

cd %BASE%
@if %errorlevel% neq 0 exit /b %errorlevel%

@echo Creating main executable...

pyinstaller aplab_runner.py --icon=aplab_icon.ico --name=%NAME% --noconsole
@if %errorlevel% neq 0 exit /b %errorlevel%

@echo Organizing files...

move %BASE%\dist\%NAME%\%NAME%.exe %BASE%\
@if %errorlevel% neq 0 exit /b %errorlevel%

rmdir /S /Q %BASE%\build
@if %errorlevel% neq 0 exit /b %errorlevel%

rmdir /S /Q %BASE%\dist
@if %errorlevel% neq 0 exit /b %errorlevel%

del /Q %BASE%\%NAME%.spec
@if %errorlevel% neq 0 exit /b %errorlevel%

@echo Creating debug executable...

pyinstaller aplab_runner.py --icon=aplab_icon.ico --name=%NAME%_debug
@if %errorlevel% neq 0 exit /b %errorlevel%

@echo Organizing files...

move %BASE%\dist\%NAME%_debug\%NAME%_debug.exe %BASE%\
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

@7z a -mx9 -tzip %ZIPFOLDER%.zip %BASE%\%NAME%.exe %BASE%\%NAME%_debug.exe README.txt
@del /Q %BASE%\%NAME%.exe %BASE%\%NAME%_debug.exe README.txt

@echo Done