from flask import Flask, jsonify
from dotenv import load_dotenv
import os
import redis
import requests
import logging
from logging.handlers import NTEventLogHandler

# Cargar variables de entorno
load_dotenv()

# Configuración del logger
def setup_logging():
    # Obtener el logger
    logger = logging.getLogger("AppPedidos")
    logger.setLevel(logging.DEBUG)  # Nivel de log

    # Crear el handler para el Visor de Eventos
    handler = NTEventLogHandler(appname="AppPedidos")

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
logger = setup_logging()

# Datos simulados de pedidos
pedidos = [
    {"id": 1, "usuario_id": 1, "producto": "Laptop", "cantidad": 1, "total": 999.99},
    {"id": 2, "usuario_id": 1, "producto": "Mouse", "cantidad": 2, "total": 49.98},
    {"id": 3, "usuario_id": 2, "producto": "Monitor", "cantidad": 1, "total": 299.99},
    {"id": 4, "usuario_id": 3, "producto": "Teclado", "cantidad": 1, "total": 89.99}
]
logger.info("Agregando pedidos")


def obtener_configuracion(service_name):
    """ Obtiene la configuración del servicio centralizado """
    try:
        response = requests.get(f"http://localhost:5002/config/{service_name}")  # Cambiar el puerto a 5002
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"No se pudo obtener la configuración para {service_name}.")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error al conectar con el servicio de configuración: {e}")
        return None
    
def verificar_usuario(usuario_id):
    """Verifica si existe un usuario consultando al servicio de usuarios"""
    try:
        puerto_usuarios = int(os.getenv('USERS_SERVICE_PORT', 5000))
        response = requests.get(f'http://localhost:{puerto_usuarios}/api/usuarios/{usuario_id}')
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"Error al verificar usuario: {e}")
        return False



@app.route('/api/pedidos', methods=['GET'])
def obtener_pedidos():
    """Endpoint para obtener todos los pedidos"""
    logger.info("Solicitando todos los pedidos.")

    # Verificar si los pedidos ya están en cache
    cached_pedidos = cache.get('pedidos')
    if cached_pedidos:
        logger.info("Pedidos obtenidos de Redis (cache).")
        return jsonify({"pedidos": pedidos, "total": len(pedidos)})

    # Si no están en cache, devolver los pedidos y guardarlos en Redis
    logger.info("Pedidos obtenidos desde base de datos, guardando en Redis.")
    cache.set('pedidos', str(pedidos))  # Convertir lista a string antes de guardarla en Redis

    return jsonify({"pedidos": pedidos, "total": len(pedidos)})

def obtener_pedidos():
    config = obtener_configuracion("pedidos_service")
    if config:
        # Usar la configuración obtenida
        return jsonify({"message": "Servicio de pedidos funcionando", "config": config}), 200
    else:
        return jsonify({"error": "No se pudo obtener la configuración"}), 500


@app.route('/api/pedidos/usuario/<int:usuario_id>', methods=['GET'])
def obtener_pedidos_usuario(usuario_id):
    """Endpoint para obtener los pedidos de un usuario específico"""
    logger.info(f"Solicitando pedidos para el usuario con ID: {usuario_id}")
    if not verificar_usuario(usuario_id):
        logger.warning(f"Usuario no encontrado: {usuario_id}")
        return jsonify({"error": "Usuario no encontrado"}), 404
    pedidos_usuario = [p for p in pedidos if p["usuario_id"] == usuario_id]
    return jsonify({
        "usuario_id": usuario_id,
        "pedidos": pedidos_usuario,
        "total_pedidos": len(pedidos_usuario)
    })



@app.route('/api/pedidos/health', methods=['GET'])
def healthcheck():
    """Endpoint para verificar el estado del servicio"""
    logger.info("Estado del servicio solicitado.")
    return jsonify({"status": "healthy", "service": "pedidos"})



if __name__ == '__main__':
    puerto = int(os.getenv('ORDERS_SERVICE_PORT', 5001))
    logger.info(f"Iniciando servicio en el puerto {puerto}.")
    app.run(port=puerto, debug=True)
