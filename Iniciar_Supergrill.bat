@echo off
echo =========================================
echo        INICIANDO SUPERGRILL PORTABLE
echo =========================================

:: Obtenemos la ruta exacta donde está guardado este .bat en la PC actual
set "RUTA_BASE=%~dp0"

echo [1/2] Levantando MariaDB...
start "MariaDB" cmd /k "cd /d "%RUTA_BASE%" && .\mariadb\bin\mysqld.exe --console --port=3307"

timeout /t 3 /nobreak > nul

echo [2/2] Levantando Django en red local...
:: Agregamos 0.0.0.0:8000 al final para permitir conexiones externas (como tu celular)
start "Django" cmd /k "cd /d "%RUTA_BASE%supergrill" && call ..\env\Scripts\activate && python manage.py runserver 0.0.0.0:8000"

timeout /t 2 /nobreak > nul
:: Tu computadora seguirá abriendo su propia ventana automáticamente en localhost
start http://127.0.0.1:8000/
exit