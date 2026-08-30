@echo off
echo =========================================
echo        INICIANDO SUPERGRILL PORTABLE
echo =========================================

:: Obtenemos la ruta exacta donde está guardado este .bat en la PC actual
set "RUTA_BASE=%~dp0"

:: 1. Extraemos la IP local real de la computadora (la de tu red WiFi o cable)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4"') do set LOCAL_IP=%%a
:: Limpiamos los espacios en blanco
set LOCAL_IP=%LOCAL_IP: =%

echo [1/2] Levantando MariaDB...
start "MariaDB" cmd /k "cd /d "%RUTA_BASE%" && .\mariadb\bin\mysqld.exe --console --port=3307"

timeout /t 3 /nobreak > nul

echo [2/2] Levantando Django en red local...
start "Django" cmd /k "cd /d "%RUTA_BASE%supergrill" && call ..\env\Scripts\activate && python manage.py runserver 0.0.0.0:5002"

timeout /t 2 /nobreak > nul

:: 2. Abrimos el navegador automáticamente con la IP real detectada
echo Tu IP en la red es: %LOCAL_IP%
start http://%LOCAL_IP%:5002/
exit