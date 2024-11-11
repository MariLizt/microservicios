import logging
from logging.handlers import NTEventLogHandler
from flask import Flask, jsonify
from dotenv import load_dotenv
import os
import redis
import json

# Cargar variables de entorno
load_dotenv()

# Configuración del logger
def setup_logging():
    # Obtener el logger
    logger = logging.getLogger("AppUsuarios")
    logger.setLevel(logging.DEBUG)  # Nivel de log

    # Crear el handler para el Visor de Eventos
    handler = NTEventLogHandler(appname="AppUsuarios")

    # Definir el formato del log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Añadir el handler al logger
    logger.addHandler(handler)

    return logger

# Usar el logger
logger = setup_logging()

# Conectar a Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
cache = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

app = Flask(__name__)

# Datos simulados de usuarios
usuarios = [
    {"id": 1, "nombre": "Ana García", "email": "ana@email.com"},
    {"id": 2, "nombre": "Carlos López", "email": "carlos@email.com"},
    {"id": 3, "nombre": "María Rodríguez", "email": "maria@email.com"}
]
logger.info("Agregando pedidos")



@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    logger.info("Solicitando todos los usuarios.")

    # Inicializar la lista de usuarios
    usuarios_respuesta = None

    # Intentar obtener los usuarios de Redis
    cached_data = cache.get('usuarios')

    if cached_data:
        logger.info("Datos obtenidos de la caché.")
        usuarios_respuesta = json.loads(cached_data)  # Convertir los datos a lista de diccionarios
    else:
        logger.info("Datos no encontrados en la caché, recuperando desde base de datos.")
        usuarios_respuesta = usuarios  # Si no está en caché, usamos los datos simulados
        # Almacenar en caché por 5 minutos
        cache.set('usuarios', json.dumps(usuarios_respuesta), ex=60*5)

    return jsonify({"usuarios": usuarios_respuesta, "total": len(usuarios_respuesta)})



@app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):
    logger.info(f"Solicitando usuario con ID: {usuario_id}")

    # Inicializar variable de respuesta
    usuario_respuesta = None

    # Verificar si el usuario está en caché
    cached_usuario = cache.get(f'usuario_{usuario_id}')
    if cached_usuario:
        logger.info(f"Usuario {usuario_id} obtenido de la caché.")
        usuario_respuesta = json.loads(cached_usuario)
    else:
        # Buscar el usuario en la "base de datos"
        usuario_respuesta = next((u for u in usuarios if u["id"] == usuario_id), None)
        if usuario_respuesta:
            logger.info(f"Usuario {usuario_id} no encontrado en caché, almacenando en caché.")
            # Almacenar en caché por 5 minutos
            cache.set(f'usuario_{usuario_id}', json.dumps(usuario_respuesta), ex=60*5)
        else:
            logger.warning(f"Usuario no encontrado: {usuario_id}")
            return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"usuario": usuario_respuesta})



@app.route('/api/usuarios/health', methods=['GET'])
def healthcheck():
    logger.info("Estado del servicio solicitado.")
    return jsonify({"status": "healthy", "service": "usuarios"})

if __name__ == '__main__':
    puerto = int(os.getenv('USERS_SERVICE_PORT', 5000))
    logger.info(f"Iniciando servicio en el puerto {puerto}.")
    app.run(port=puerto, debug=True)
