@echo off
echo Iniciando servicios de microservicios...

REM Levanta los servicios de Docker Compose en segundo plano (detached mode)
echo Iniciando servicios con Docker Compose...
docker-compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo Error al iniciar los contenedores de Docker.
    exit /b 1
)
echo Docker Compose ha iniciado los servicios en segundo plano.
REM Espera un momento para asegurar que Redis esté en funcionamiento
timeout /t 5 /nobreak

REM Inicia el servicio de usuarios
start cmd /k "cd /d %~dp0 && venv\Scripts\activate && python servicio_usuarios.py"

REM Espera un momento antes de iniciar el siguiente servicio
timeout /t 2 /nobreak

REM Inicia el servicio de pedidos
start cmd /k "cd /d %~dp0 && venv\Scripts\activate && python servicio_pedidos.py"

echo Servicios iniciados. Puedes acceder a:
echo Usuarios: http://localhost:5000/api/usuarios
echo Pedidos: http://localhost:5001/api/pedidos
