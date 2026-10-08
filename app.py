from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_from_directory,
    redirect,
    url_for,
    session
)

from werkzeug.utils import secure_filename

import os
import hmac
from datetime import datetime


app = Flask(__name__)

# =========================================================
# CONFIGURAÇÕES DE SEGURANÇA
# =========================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "chave-temporaria-rarei"
)

ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "rarei123"
)


# =========================================================
# PASTAS
# =========================================================

PASTA_FOTOS = os.path.join(
    "uploads",
    "fotos"
)

PASTA_VIDEOS = os.path.join(
    "uploads",
    "videos"
)

os.makedirs(
    PASTA_FOTOS,
    exist_ok=True
)

os.makedirs(
    PASTA_VIDEOS,
    exist_ok=True
)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def inicio():

    return render_template(
        "index.html"
    )


# =========================================================
# FOTOS
# =========================================================

@app.route("/fotos")
def fotos():

    arquivos = os.listdir(
        PASTA_FOTOS
    )

    arquivos.sort(
        reverse=True
    )

    return render_template(
        "fotos.html",
        arquivos=arquivos
    )


# =========================================================
# VÍDEOS
# =========================================================

@app.route("/videos")
def videos():

    arquivos = os.listdir(
        PASTA_VIDEOS
    )

    arquivos.sort(
        reverse=True
    )

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
# UPLOAD DE FOTO
# =========================================================

@app.route(
    "/upload/foto",
    methods=["POST"]
)
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

    permitidas = [
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    ]

    if extensao not in permitidas:

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

    arquivo.save(
        caminho
    )

    return jsonify({
        "sucesso": True,
        "arquivo": nome_final
    })


# =========================================================
# UPLOAD DE VÍDEO
# =========================================================

@app.route(
    "/upload/video",
    methods=["POST"]
)
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

    permitidas = [
        ".mp4",
        ".avi",
        ".mov"
    ]

    if extensao not in permitidas:

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

    arquivo.save(
        caminho
    )

    return jsonify({
        "sucesso": True,
        "arquivo": nome_final
    })


# =========================================================
# MOSTRAR FOTOS
# =========================================================

@app.route(
    "/uploads/fotos/<filename>"
)
def mostrar_foto(filename):

    return send_from_directory(
        PASTA_FOTOS,
        filename
    )


# =========================================================
# MOSTRAR VÍDEOS
# =========================================================

@app.route(
    "/uploads/videos/<filename>"
)
def mostrar_video(filename):

    return send_from_directory(
        PASTA_VIDEOS,
        filename
    )


# =========================================================
# LOGIN DO ADMIN
# =========================================================

@app.route(
    "/admin",
    methods=["GET", "POST"]
)
def admin():

    if session.get("admin_logado"):

        return redirect(
            url_for(
                "painel_admin"
            )
        )

    erro = None

    if request.method == "POST":

        senha = request.form.get(
            "senha",
            ""
        )

        if hmac.compare_digest(
            senha,
            ADMIN_PASSWORD
        ):

            session[
                "admin_logado"
            ] = True

            return redirect(
                url_for(
                    "painel_admin"
                )
            )

        erro = "Senha incorreta."

    return render_template(
        "admin_login.html",
        erro=erro
    )


# =========================================================
# PAINEL ADMIN
# =========================================================

@app.route("/admin/painel")
def painel_admin():

    if not session.get(
        "admin_logado"
    ):

        return redirect(
            url_for(
                "admin"
            )
        )

    fotos = os.listdir(
        PASTA_FOTOS
    )

    videos = os.listdir(
        PASTA_VIDEOS
    )

    fotos.sort(
        reverse=True
    )

    videos.sort(
        reverse=True
    )

    return render_template(
        "admin.html",
        fotos=fotos,
        videos=videos
    )


# =========================================================
# EXCLUIR FOTO
# =========================================================

@app.route(
    "/admin/excluir/foto/<filename>",
    methods=["POST"]
)
def excluir_foto(filename):

    if not session.get(
        "admin_logado"
    ):

        return redirect(
            url_for(
                "admin"
            )
        )

    nome = os.path.basename(
        filename
    )

    caminho = os.path.join(
        PASTA_FOTOS,
        nome
    )

    if os.path.isfile(
        caminho
    ):

        os.remove(
            caminho
        )

    return redirect(
        url_for(
            "painel_admin"
        )
    )


# =========================================================
# EXCLUIR VÍDEO
# =========================================================

@app.route(
    "/admin/excluir/video/<filename>",
    methods=["POST"]
)
def excluir_video(filename):

    if not session.get(
        "admin_logado"
    ):

        return redirect(
            url_for(
                "admin"
            )
        )

    nome = os.path.basename(
        filename
    )

    caminho = os.path.join(
        PASTA_VIDEOS,
        nome
    )

    if os.path.isfile(
        caminho
    ):

        os.remove(
            caminho
        )

    return redirect(
        url_for(
            "painel_admin"
        )
    )


# =========================================================
# LOGOUT ADMIN
# =========================================================

@app.route("/admin/sair")
def sair_admin():

    session.pop(
        "admin_logado",
        None
    )

    return redirect(
        url_for(
            "admin"
        )
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
