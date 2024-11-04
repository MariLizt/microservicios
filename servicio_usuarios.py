from flask import Flask, jsonify
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Datos simulados de usuarios
usuarios = [
    {"id": 1, "nombre": "Ana García", "email": "ana@email.com"},
    {"id": 2, "nombre": "Carlos López", "email": "carlos@email.com"},
    {"id": 3, "nombre": "María Rodríguez", "email": "maria@email.com"}
]

@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    """Endpoint para obtener todos los usuarios"""
    return jsonify({"usuarios": usuarios, "total": len(usuarios)})

@app.route('/api/usuarios/<int:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):
    """Endpoint para obtener un usuario específico por ID"""
    usuario = next((u for u in usuarios if u["id"] == usuario_id), None)
    if usuario:
        return jsonify({"usuario": usuario})
    return jsonify({"error": "Usuario no encontrado"}), 404

@app.route('/api/usuarios/health', methods=['GET'])
def healthcheck():
    """Endpoint para verificar el estado del servicio"""
    return jsonify({"status": "healthy", "service": "usuarios"})

if __name__ == '__main__':
    puerto = int(os.getenv('USERS_SERVICE_PORT', 5000))
    app.run(port=puerto, debug=True)
