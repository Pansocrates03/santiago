from flask import Flask, jsonify
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
swagger = Swagger(app)

@app.route('/chart', methods=['GET'])
def get_chart():
    """
    Obtiene un gráfico en formato imagen
    ---
    responses:
      200:
        description: Devuelve un gráfico
        schema:
          type: "string"
    """
    # Aquí iría tu lógica para generar el gráfico
    return jsonify({"message": "Aquí iría tu gráfico"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
