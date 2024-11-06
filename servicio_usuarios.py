import logging
from logging.handlers import NTEventLogHandler
from flask import Flask, jsonify
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración del logger
def setup_logging():
    # Obtener el logger
    logger = logging.getLogger("AppMicroservicios")
    logger.setLevel(logging.DEBUG)  # Nivel de log

    # Crear el handler para el Visor de Eventos
    handler = NTEventLogHandler(appname="AppMicroservicios")

    # Definir el formato del log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Añadir el handler al logger
    logger.addHandler(handler)

    return logger

# Usar el logger
logger = setup_logging()

# Mensaje de logs
logger.info("Este es un mensaje de información.")
logger.warning("Este es un mensaje de advertencia.")
logger.error("Este es un mensaje de error.")

app = Flask(__name__)
logger = setup_logging()

# Datos simulados de usuarios
usuarios = [
    {"id": 1, "nombre": "Ana García", "email": "ana@email.com"},
    {"id": 2, "nombre": "Carlos López", "email": "carlos@email.com"},
    {"id": 3, "nombre": "María Rodríguez", "email": "maria@email.com"}
]

@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    logger.info("Solicitando todos los usuarios.")
    return jsonify({"usuarios": usuarios, "total": len(usuarios)})

@app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):
    logger.info(f"Solicitando usuario con ID: {usuario_id}")
    usuario = next((u for u in usuarios if u["id"] == usuario_id), None)
    if usuario:
        return jsonify({"usuario": usuario})
    logger.warning(f"Usuario no encontrado: {usuario_id}")
    return jsonify({"error": "Usuario no encontrado"}), 404

@app.route('/api/usuarios/health', methods=['GET'])
def healthcheck():
    logger.info("Estado del servicio solicitado.")
    return jsonify({"status": "healthy", "service": "usuarios"})

if __name__ == '__main__':
    puerto = int(os.getenv('USERS_SERVICE_PORT', 5000))
    logger.info(f"Iniciando servicio en el puerto {puerto}.")
    app.run(port=puerto, debug=True)
