@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation with correct Python environment

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=C:\Users\Carlos\anaconda3\envs\scientific_general\python.exe -m sphinx
)
set SOURCEDIR=.
set BUILDDIR=_build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The Python environment or Sphinx was not found. Make sure you have:
	echo.1. Anaconda installed at C:\Users\Carlos\anaconda3\
	echo.2. The 'scientific_general' environment created
	echo.3. Sphinx installed in that environment
	echo.
	echo.You can install Sphinx with:
	echo.conda activate scientific_general
	echo.pip install sphinx sphinx-rtd-theme
	exit /b 1
)

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
