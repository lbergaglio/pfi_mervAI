import os
import logging
from flask import Flask, request, jsonify
from interface import adaptar_texto

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route("/api/adaptar-texto", methods=["POST"])
def adaptar():
    """
    Adapta un texto proporcionado a un nivel específico.
    Espera un payload JSON con las claves "texto" y "nivel".
    ---
    responses:
      200:
        description: Texto adaptado con éxito.
      400:
        description: Request incorrecto - El JSON falta, está mal formado o faltan claves.
      500:
        description: Error interno del servidor.
    """
    if not request.is_json:
        logging.warning("El request recibido no es un JSON.")
        return jsonify({"error": "El cuerpo del request debe ser de tipo JSON"}), 400

    data = request.get_json()
    texto = data.get("texto")
    nivel = data.get("nivel")

    if not texto or not nivel:
        logging.warning("Faltan 'texto' o 'nivel' en el cuerpo del request.")
        return jsonify({"error": "Faltan las claves 'texto' o 'nivel' en el cuerpo del request"}), 400

    if not isinstance(texto, str):
        logging.warning(f"'texto' no es un string, es de tipo {type(texto)}")
        return jsonify({"error": "'texto' debe ser un string"}), 400

    if not isinstance(nivel, str):
        logging.warning(f"'nivel' no es un string, es de tipo {type(nivel)}")
        return jsonify({"error": "'nivel' debe ser un string"}), 400

    logging.info(f"Request recibido para adaptar texto al nivel: {nivel}")

    try:
        resultado = adaptar_texto(texto, nivel)
        logging.info("Adaptación de texto completada con éxito.")
        return jsonify({"adaptado": resultado})
    except Exception as e:
        logging.error(f"Error durante la adaptación del texto: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error interno durante la adaptación del texto."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("FLASK_PORT", 5001))
    app.run(host="0.0.0.0", port=port)
