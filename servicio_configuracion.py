# servicio_configuracion.py
from flask import Flask, jsonify

app = Flask(__name__)

config = {
    "usuario_service": {
        "port": 5000,
        "url": "http://localhost:5000",
        "redis_host": "localhost",
        "redis_port": 6379
    },
    "pedidos_service": {
        "port": 5001,
        "url": "http://localhost:5001",
        "redis_host": "localhost",
        "redis_port": 6380
    }
}

@app.route('/config/<service_name>', methods=['GET'])
def get_config(service_name):
    if service_name in config:
        return jsonify(config[service_name]), 200
    else:
        return jsonify({"error": "Servicio no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
