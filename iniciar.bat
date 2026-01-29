@echo off
title INMO - Iniciador

echo.
echo ============================================
echo    INMO - Sistema Inmobiliario Paraguay
echo    Asistente IA Inmobiliario
echo ============================================
echo.

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo         Descargalo desde: https://python.org
    pause
    exit /b 1
)
echo [OK] Python encontrado

REM Verificar si Node.js esta instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no esta instalado o no esta en el PATH
    echo         Descargalo desde: https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js encontrado

REM Verificar archivo .env
if not exist ".env" (
    if exist ".env.example" (
        echo [AVISO] Archivo .env no encontrado, creando desde .env.example...
        copy ".env.example" ".env" >nul
        echo [INFO] Por favor edita el archivo .env con tus API keys
    )
)

echo.
echo [1/4] Instalando dependencias del backend...
cd backend
pip install -r requirements.txt -q 2>nul
cd ..
echo       Completado

echo [2/4] Instalando dependencias del frontend...
cd frontend
call npm install --silent 2>nul
cd ..
echo       Completado

echo.
echo [3/4] Iniciando backend (FastAPI en puerto 8000)...
start "INMO Backend" cmd /k "cd backend && python main.py"

echo [4/4] Esperando que el backend inicie...
timeout /t 4 /nobreak >nul

echo      Iniciando frontend (Next.js en puerto 3000)...
start "INMO Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================
echo    INMO esta corriendo!
echo ============================================
echo.
echo    Frontend:  http://localhost:3000
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo.
echo    Para detener: cierra las ventanas
echo ============================================
echo.

REM Abrir navegador automaticamente
timeout /t 2 /nobreak >nul
start http://localhost:3000

echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul
