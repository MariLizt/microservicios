@echo off
echo Iniciando servicios de microservicios...
start cmd /k "cd /d %~dp0 && venv\Scripts\activate && python
servicio_usuarios.py"
timeout /t 2
start cmd /k "cd /d %~dp0 && venv\Scripts\activate && python
servicio_pedidos.py"
echo Servicios iniciados. Puedes acceder a:
echo Usuarios: http://localhost:5000/usuarios
echo Pedidos: http://localhost:5001/pedidos