@echo off
REM Waterfall build script for Nebula Rivulet (Windows)
REM Build order: fabric -> rivulet -> vertex

echo ==========================================
echo Building Nebula Rivulet - Waterfall Model
echo ==========================================

REM Step 1: Build fabric (base layer)
echo.
echo Step 1/3: Building nebula.fabric...
cd fabric
python setup.py sdist bdist_wheel
if %errorlevel% neq 0 exit /b %errorlevel%
@REM echo [32m✓ nebula.fabric-3.10.0 built successfully[0m
cd ..

REM Step 2: Install fabric and build rivulet (pipeline layer)
echo.
echo Step 2/3: Building nebula.rivulet...
@REM pip install fabric\dist\nebula_fabric-3.10.0-py3-none-any.whl --force-reinstall
if %errorlevel% neq 0 exit /b %errorlevel%
cd rivulet
python setup.py sdist bdist_wheel
if %errorlevel% neq 0 exit /b %errorlevel%
@REM echo [32m✓ nebula.rivulet-3.10.0 built successfully[0m
cd ..

REM Step 3: Install rivulet and build vertex (API layer)
echo.
echo Step 3/3: Building nebula.vertex...
@REM pip install rivulet\dist\nebula_rivulet-3.10.0-py3-none-any.whl --force-reinstall
if %errorlevel% neq 0 exit /b %errorlevel%
cd vertex
python setup.py sdist bdist_wheel
if %errorlevel% neq 0 exit /b %errorlevel%
@REM echo [32m✓ nebula.vertex-3.10.0 built successfully[0m
cd ..

echo.
echo ==========================================
echo Build Complete!
echo ==========================================
echo Wheel files created:
echo   1. fabric\dist\nebula.fabric-3.10.0-py3-none-any.whl
echo   2. rivulet\dist\nebula.rivulet-3.10.0-py3-none-any.whl
echo   3. vertex\dist\nebula.vertex-3.10.0-py3-none-any.whl
echo.
echo Installation order:
echo   pip install fabric\dist\nebula.fabric-3.10.0-py3-none-any.whl
echo   pip install rivulet\dist\nebula.rivulet-3.10.0-py3-none-any.whl
echo   pip install vertex\dist\nebula.vertex-3.10.0-py3-none-any.whl
echo.
echo Running the server:
echo   Set environment: set NEBULA_RIVULET_HOME=C:\Nebula.Rivulet\db
echo   Run server: uvicorn main:app --host 0.0.0.0 --port 8000
