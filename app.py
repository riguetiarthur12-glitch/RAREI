from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import json
import hmac
from datetime import datetime

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "chave-temporaria-rarei")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "rarei123")

PASTA_FOTOS = os.path.join("uploads", "fotos")
PASTA_VIDEOS = os.path.join("uploads", "videos")
PASTA_ANALISES = os.path.join("dados", "analises")

os.makedirs(PASTA_FOTOS, exist_ok=True)
os.makedirs(PASTA_VIDEOS, exist_ok=True)
os.makedirs(PASTA_ANALISES, exist_ok=True)

def carregar_analises():
    analises = []

    for nome in os.listdir(PASTA_ANALISES):
        if not nome.lower().endswith(".json"):
            continue

        caminho = os.path.join(PASTA_ANALISES, nome)

        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            if isinstance(dados, dict):
                dados["arquivo_json"] = nome
                analises.append(dados)

        except (OSError, json.JSONDecodeError):
            continue

    analises.sort(
        key=lambda item: item.get("recebido_em_iso", ""),
        reverse=True
    )

    return analises

def salvar_json_recebido(arquivo_json, nome_foto):
    try:
        conteudo = arquivo_json.read()
        dados = json.loads(conteudo.decode("utf-8"))

    except (UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(dados, dict):
        return None

    agora = datetime.now()

    dados["arquivo_imagem"] = nome_foto
    dados["recebido_em"] = agora.strftime("%d/%m/%Y %H:%M:%S")
    dados["recebido_em_iso"] = agora.isoformat(timespec="seconds")

    nome_json = os.path.splitext(nome_foto)[0] + ".json"
    caminho_json = os.path.join(PASTA_ANALISES, nome_json)

    with open(caminho_json, "w", encoding="utf-8") as destino:
        json.dump(
            dados,
            destino,
            ensure_ascii=False,
            indent=2
        )

    dados["arquivo_json"] = nome_json

    return dados

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/fotos")
def fotos():
    arquivos = os.listdir(PASTA_FOTOS)
    arquivos.sort(reverse=True)

    return render_template(
        "fotos.html",
        arquivos=arquivos
    )

@app.route("/videos")
def videos():
    arquivos = os.listdir(PASTA_VIDEOS)
    arquivos.sort(reverse=True)

    return render_template(
        "videos.html",
        arquivos=arquivos
    )

@app.route("/catalogo")
def catalogo():
    analises = carregar_analises()

    animais = [
        item
        for item in analises
        if item.get("animal_detectado", False)
        and item.get("status") == "catalogado_automaticamente"
    ]

    return render_template(
        "catalogo.html",
        animais=animais
    )

@app.route("/upload/foto", methods=["POST"])
def upload_foto():
    if "arquivo" not in request.files:
        return jsonify({
            "sucesso": False,
            "erro": "Nenhuma foto recebida."
        }), 400

    arquivo = request.files["arquivo"]

    if arquivo.filename == "":
        return jsonify({
            "sucesso": False,
            "erro": "Foto sem nome."
        }), 400

    extensao = os.path.splitext(arquivo.filename)[1].lower()

    if extensao not in {".jpg", ".jpeg", ".png", ".webp"}:
        return jsonify({
            "sucesso": False,
            "erro": "Formato de foto inválido."
        }), 400

    nome_original = secure_filename(arquivo.filename)
    prefixo = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    nome_foto = prefixo + "_" + nome_original

    caminho_foto = os.path.join(
        PASTA_FOTOS,
        nome_foto
    )

    arquivo.save(caminho_foto)

    analise_salva = False

    if "analise_json" in request.files:
        analise_json = request.files["analise_json"]

        if analise_json.filename:
            resultado = salvar_json_recebido(
                analise_json,
                nome_foto
            )

            analise_salva = resultado is not None

    return jsonify({
        "sucesso": True,
        "arquivo": nome_foto,
        "analise_json_salva": analise_salva
    })

@app.route("/upload/video", methods=["POST"])
def upload_video():
    if "arquivo" not in request.files:
        return jsonify({
            "sucesso": False,
            "erro": "Nenhum vídeo recebido."
        }), 400

    arquivo = request.files["arquivo"]

    if arquivo.filename == "":
        return jsonify({
            "sucesso": False,
            "erro": "Vídeo sem nome."
        }), 400

    extensao = os.path.splitext(arquivo.filename)[1].lower()

    if extensao not in {".mp4", ".avi", ".mov"}:
        return jsonify({
            "sucesso": False,
            "erro": "Formato de vídeo inválido."
        }), 400

    nome_original = secure_filename(arquivo.filename)
    prefixo = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    nome_video = prefixo + "_" + nome_original

    caminho_video = os.path.join(
        PASTA_VIDEOS,
        nome_video
    )

    arquivo.save(caminho_video)

    return jsonify({
        "sucesso": True,
        "arquivo": nome_video
    })

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

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("admin_logado"):
        return redirect(
            url_for("painel_admin")
        )

    erro = None

    if request.method == "POST":
        senha = request.form.get("senha", "")

        if hmac.compare_digest(
            senha,
            ADMIN_PASSWORD
        ):
            session["admin_logado"] = True

            return redirect(
                url_for("painel_admin")
            )

        erro = "Senha incorreta."

    return render_template(
        "admin_login.html",
        erro=erro
    )

@app.route("/admin/painel")
def painel_admin():
    if not session.get("admin_logado"):
        return redirect(
            url_for("admin")
        )

    fotos = os.listdir(PASTA_FOTOS)
    videos = os.listdir(PASTA_VIDEOS)

    fotos.sort(reverse=True)
    videos.sort(reverse=True)

    return render_template(
        "admin.html",
        fotos=fotos,
        videos=videos,
        analises=carregar_analises()
    )

@app.route("/admin/excluir/foto/<filename>", methods=["POST"])
def excluir_foto(filename):
    if not session.get("admin_logado"):
        return redirect(
            url_for("admin")
        )

    nome = os.path.basename(filename)
    caminho = os.path.join(PASTA_FOTOS, nome)

    if os.path.isfile(caminho):
        os.remove(caminho)

    for analise in carregar_analises():
        if analise.get("arquivo_imagem") == nome:
            nome_json = analise.get("arquivo_json")

            if nome_json:
                caminho_json = os.path.join(
                    PASTA_ANALISES,
                    os.path.basename(nome_json)
                )

                if os.path.isfile(caminho_json):
                    os.remove(caminho_json)

    return redirect(
        url_for("painel_admin")
    )

@app.route("/admin/excluir/video/<filename>", methods=["POST"])
def excluir_video(filename):
    if not session.get("admin_logado"):
        return redirect(
            url_for("admin")
        )

    nome = os.path.basename(filename)
    caminho = os.path.join(PASTA_VIDEOS, nome)

    if os.path.isfile(caminho):
        os.remove(caminho)

    return redirect(
        url_for("painel_admin")
    )

@app.route("/admin/excluir/analise/<filename>", methods=["POST"])
def excluir_analise(filename):
    if not session.get("admin_logado"):
        return redirect(
            url_for("admin")
        )

    nome = os.path.basename(filename)
    caminho = os.path.join(PASTA_ANALISES, nome)

    if os.path.isfile(caminho):
        os.remove(caminho)

    return redirect(
        url_for("painel_admin")
    )

@app.route("/admin/sair")
def sair_admin():
    session.pop("admin_logado", None)

    return redirect(
        url_for("admin")
    )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
