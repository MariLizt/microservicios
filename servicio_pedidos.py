from flask import Flask, jsonify
from dotenv import load_dotenv
import os
import requests

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Datos simulados de pedidos
pedidos = [
    {"id": 1, "usuario_id": 1, "producto": "Laptop", "cantidad": 1, "total": 999.99},
    {"id": 2, "usuario_id": 1, "producto": "Mouse", "cantidad": 2, "total": 49.98},
    {"id": 3, "usuario_id": 2, "producto": "Monitor", "cantidad": 1, "total": 299.99},
    {"id": 4, "usuario_id": 3, "producto": "Teclado", "cantidad": 1, "total": 89.99}
]

def verificar_usuario(usuario_id):
    """Verifica si existe un usuario consultando al servicio de usuarios"""
    try:
        puerto_usuarios = int(os.getenv('USERS_SERVICE_PORT', 5000))
        response = requests.get(f'http://localhost:{puerto_usuarios}/usuarios/{usuario_id}')
        return response.status_code == 200
    except requests.RequestException:
        return False

@app.route('/pedidos', methods=['GET'])
def obtener_pedidos():
    """Endpoint para obtener todos los pedidos"""
    return jsonify({"pedidos": pedidos, "total": len(pedidos)})

@app.route('/pedidos/usuario/<int:usuario_id>', methods=['GET'])
def obtener_pedidos_usuario(usuario_id):
    """Endpoint para obtener los pedidos de un usuario específico"""
    if not verificar_usuario(usuario_id):
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    pedidos_usuario = [p for p in pedidos if p["usuario_id"] == usuario_id]
    return jsonify({
        "usuario_id": usuario_id,
        "pedidos": pedidos_usuario,
        "total_pedidos": len(pedidos_usuario)
    })

@app.route('/health', methods=['GET'])
def healthcheck():
    """Endpoint para verificar el estado del servicio"""
    return jsonify({"status": "healthy", "service": "pedidos"})

if __name__ == '__main__':
    puerto = int(os.getenv('ORDERS_SERVICE_PORT', 5001))
    app.run(port=puerto, debug=True)