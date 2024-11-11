import os
import logging
import requests
import redis
import json
from flask import Flask, jsonify

# Configuración del logger
def setup_logging():
    logger = logging.getLogger("AppUsuarios")
    logger.setLevel(logging.DEBUG)  # Nivel de log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Para este ejemplo, usaremos consola
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

logger = setup_logging()

# Conectar a Redis
def obtener_configuracion(service_name):
    """ Obtiene la configuración del servicio centralizado """
    try:
        response = requests.get(f"http://localhost:5002/config/{service_name}")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"No se pudo obtener la configuración para {service_name}.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al conectar con el servicio de configuración: {e}")
        return None

# Inicializamos el Flask app
app = Flask(__name__)

# Obtener la configuración del servicio de usuario desde el servicio central
config = obtener_configuracion("usuario_service")
if config:
    # Establecer variables de entorno a partir de la configuración obtenida
    os.environ['USERS_SERVICE_PORT'] = str(config.get('port', 5000))
    os.environ['REDIS_HOST'] = config.get('redis_host', 'localhost')
    os.environ['REDIS_PORT'] = str(config.get('redis_port', 6379))
    logger.info(f"Configuración cargada desde el servicio de configuración.")
else:
    logger.warning("No se pudo cargar la configuración desde el servicio central, usando valores por defecto.")

# Conectar a Redis usando las variables de entorno
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
cache = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

# Datos simulados de usuarios
usuarios = [
    {"id": 1, "nombre": "Ana García", "email": "ana@email.com"},
    {"id": 2, "nombre": "Carlos López", "email": "carlos@email.com"},
    {"id": 3, "nombre": "María Rodríguez", "email": "maria@email.com"}
]

# Endpoint para obtener los usuarios
@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    logger.info("Solicitando todos los usuarios.")
    usuarios_respuesta = None

    # Intentar obtener los usuarios de Redis
    cached_data = cache.get('usuarios')

    if cached_data:
        logger.info("Datos obtenidos de la caché.")
        usuarios_respuesta = json.loads(cached_data)
    else:
        logger.info("Datos no encontrados en la caché, recuperando desde base de datos.")
        usuarios_respuesta = usuarios
        # Almacenar en caché por 5 minutos
        cache.set('usuarios', json.dumps(usuarios_respuesta), ex=60*5)

    return jsonify({"usuarios": usuarios_respuesta, "total": len(usuarios_respuesta)})

@app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):
    logger.info(f"Solicitando usuario con ID: {usuario_id}")
    usuario_respuesta = None

    cached_usuario = cache.get(f'usuario_{usuario_id}')
    if cached_usuario:
        logger.info(f"Usuario {usuario_id} obtenido de la caché.")
        usuario_respuesta = json.loads(cached_usuario)
    else:
        usuario_respuesta = next((u for u in usuarios if u["id"] == usuario_id), None)
        if usuario_respuesta:
            logger.info(f"Usuario {usuario_id} no encontrado en caché, almacenando en caché.")
            cache.set(f'usuario_{usuario_id}', json.dumps(usuario_respuesta), ex=60*5)
        else:
            logger.warning(f"Usuario no encontrado: {usuario_id}")
            return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"usuario": usuario_respuesta})

# Healthcheck
@app.route('/api/usuarios/health', methods=['GET'])
def healthcheck():
    logger.info("Estado del servicio solicitado.")
    return jsonify({"status": "healthy", "service": "usuarios"})

# Configurar el puerto de ejecución desde las variables de entorno
if __name__ == '__main__':
    puerto = int(os.getenv('USERS_SERVICE_PORT', 5000))
    logger.info(f"Iniciando servicio en el puerto {puerto}.")
    app.run(port=puerto, debug=True)
