from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime


app = Flask(__name__)

# =========================================================
# PASTAS DE UPLOAD
# =========================================================

PASTA_FOTOS = os.path.join("uploads", "fotos")
PASTA_VIDEOS = os.path.join("uploads", "videos")

os.makedirs(PASTA_FOTOS, exist_ok=True)
os.makedirs(PASTA_VIDEOS, exist_ok=True)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def inicio():
    return render_template("index.html")


# =========================================================
# PÁGINA DE FOTOS
# =========================================================

@app.route("/fotos")
def fotos():

    arquivos = os.listdir(PASTA_FOTOS)

    arquivos.sort(reverse=True)

    return render_template(
        "fotos.html",
        arquivos=arquivos
    )


# =========================================================
# PÁGINA DE VÍDEOS
# =========================================================

@app.route("/videos")
def videos():

    arquivos = os.listdir(PASTA_VIDEOS)

    arquivos.sort(reverse=True)

    return render_template(
        "videos.html",
        arquivos=arquivos
    )


# =========================================================
# CATÁLOGO
# =========================================================

@app.route("/catalogo")
def catalogo():

    return """
    <h1>Catálogo R.A.R.E.I</h1>
    <p>A identificação por IA será adicionada aqui.</p>
    """


# =========================================================
# RECEBER FOTO
# =========================================================

@app.route("/upload/foto", methods=["POST"])
def upload_foto():

    if "arquivo" not in request.files:

        return jsonify({
            "sucesso": False,
            "erro": "Nenhum arquivo recebido."
        }), 400

    arquivo = request.files["arquivo"]

    if arquivo.filename == "":

        return jsonify({
            "sucesso": False,
            "erro": "Arquivo sem nome."
        }), 400

    extensao = os.path.splitext(
        arquivo.filename
    )[1].lower()

    extensoes_permitidas = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ]

    if extensao not in extensoes_permitidas:

        return jsonify({
            "sucesso": False,
            "erro": "Formato de imagem não permitido."
        }), 400

    nome_original = secure_filename(
        arquivo.filename
    )

    data = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    nome_final = (
        data
        + "_"
        + nome_original
    )

    caminho = os.path.join(
        PASTA_FOTOS,
        nome_final
    )

    arquivo.save(caminho)

    return jsonify({
        "sucesso": True,
        "tipo": "foto",
        "arquivo": nome_final
    })


# =========================================================
# RECEBER VÍDEO
# =========================================================

@app.route("/upload/video", methods=["POST"])
def upload_video():

    if "arquivo" not in request.files:

        return jsonify({
            "sucesso": False,
            "erro": "Nenhum arquivo recebido."
        }), 400

    arquivo = request.files["arquivo"]

    if arquivo.filename == "":

        return jsonify({
            "sucesso": False,
            "erro": "Arquivo sem nome."
        }), 400

    extensao = os.path.splitext(
        arquivo.filename
    )[1].lower()

    extensoes_permitidas = [
        ".mp4",
        ".avi",
        ".mov"
    ]

    if extensao not in extensoes_permitidas:

        return jsonify({
            "sucesso": False,
            "erro": "Formato de vídeo não permitido."
        }), 400

    nome_original = secure_filename(
        arquivo.filename
    )

    data = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    nome_final = (
        data
        + "_"
        + nome_original
    )

    caminho = os.path.join(
        PASTA_VIDEOS,
        nome_final
    )

    arquivo.save(caminho)

    return jsonify({
        "sucesso": True,
        "tipo": "video",
        "arquivo": nome_final
    })


# =========================================================
# MOSTRAR ARQUIVOS
# =========================================================

@app.route("/uploads/fotos/<filename>")
def mostrar_foto(filename):

    return send_from_directory(
        PASTA_FOTOS,
        filename
    )


@app.route("/uploads/videos/<filename>")
def mostrar_video(filename):

    return send_from_directory(
        PASTA_VIDEOS,
        filename
    )


# =========================================================
# EXECUTAR LOCALMENTE
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
