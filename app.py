# app.py
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
PASTA_DADOS = "dados"
ARQUIVO_ANALISES = os.path.join(PASTA_DADOS, "analises.json")

os.makedirs(PASTA_FOTOS, exist_ok=True)
os.makedirs(PASTA_VIDEOS, exist_ok=True)
os.makedirs(PASTA_DADOS, exist_ok=True)

def carregar_analises():
    if not os.path.isfile(ARQUIVO_ANALISES):
        return []
    try:
        with open(ARQUIVO_ANALISES, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if isinstance(dados, list):
            return dados
    except (json.JSONDecodeError, OSError):
        pass
    return []

def salvar_analises(analises):
    temp = ARQUIVO_ANALISES + ".tmp"
    with open(temp, "w", encoding="utf-8") as arquivo:
        json.dump(analises, arquivo, ensure_ascii=False, indent=2)
    os.replace(temp, ARQUIVO_ANALISES)

def nome_comum_pt(nome_modelo):
    traducoes = {
        "capybara": "Capivara",
        "lesser capybara": "Capivara-menor",
        "jaguar": "Onça-pintada",
        "puma": "Onça-parda",
        "ocelot": "Jaguatirica",
        "giant anteater": "Tamanduá-bandeira",
        "lowland tapir": "Anta",
        "nine-banded armadillo": "Tatu-galinha",
        "white-tailed deer": "Veado-de-cauda-branca"
    }
    if not nome_modelo:
        return "Animal não identificado"
    chave = nome_modelo.strip().lower()
    return traducoes.get(chave, nome_modelo.replace("_", " ").strip().title())

def registrar_analise(analise, nome_arquivo):
    if not isinstance(analise, dict) or not analise.get("sucesso"):
        return None

    analises = carregar_analises()
    agora = datetime.now()

    registro = {
        "id": agora.strftime("%Y%m%d%H%M%S%f"),
        "arquivo": nome_arquivo,
        "data_hora": agora.strftime("%d/%m/%Y %H:%M:%S"),
        "animal_detectado": bool(analise.get("animal_detectado", False)),
        "nome_comum_modelo": analise.get("nome_comum_modelo"),
        "nome_comum_pt": nome_comum_pt(analise.get("nome_comum_modelo")),
        "nome_cientifico": analise.get("nome_cientifico"),
        "genero": analise.get("genero"),
        "especie": analise.get("especie"),
        "familia": analise.get("familia"),
        "ordem": analise.get("ordem"),
        "confianca_especie_percentual": analise.get("confianca_especie_percentual", 0),
        "confianca_deteccao_percentual": analise.get("confianca_deteccao_percentual", 0),
        "status": analise.get("status", "nao_identificado"),
        "modelo": analise.get("modelo"),
        "fonte_predicao": analise.get("fonte_predicao"),
        "pais": analise.get("pais", "BRA")
    }

    analises.insert(0, registro)
    salvar_analises(analises)
    return registro

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/fotos")
def fotos():
    arquivos = os.listdir(PASTA_FOTOS)
    arquivos.sort(reverse=True)
    return render_template("fotos.html", arquivos=arquivos)

@app.route("/videos")
def videos():
    arquivos = os.listdir(PASTA_VIDEOS)
    arquivos.sort(reverse=True)
    return render_template("videos.html", arquivos=arquivos)

@app.route("/catalogo")
def catalogo():
    analises = carregar_analises()

    catalogados = [
        item for item in analises
        if item.get("animal_detectado")
        and item.get("status") == "catalogado_automaticamente"
    ]

    return render_template("catalogo.html", animais=catalogados)

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

    extensao = os.path.splitext(arquivo.filename)[1].lower()
    permitidas = [".jpg", ".jpeg", ".png", ".webp"]

    if extensao not in permitidas:
        return jsonify({
            "sucesso": False,
            "erro": "Formato de imagem não permitido."
        }), 400

    nome_original = secure_filename(arquivo.filename)
    data = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    nome_final = data + "_" + nome_original
    caminho = os.path.join(PASTA_FOTOS, nome_final)

    arquivo.save(caminho)

    registro_ia = None
    analise_ia_texto = request.form.get("analise_ia", "")

    if analise_ia_texto:
        try:
            analise_ia = json.loads(analise_ia_texto)
            registro_ia = registrar_analise(analise_ia, nome_final)
        except json.JSONDecodeError:
            pass

    return jsonify({
        "sucesso": True,
        "tipo": "foto",
        "arquivo": nome_final,
        "analise_registrada": registro_ia is not None
    })

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

    extensao = os.path.splitext(arquivo.filename)[1].lower()
    permitidas = [".mp4", ".avi", ".mov"]

    if extensao not in permitidas:
        return jsonify({
            "sucesso": False,
            "erro": "Formato de vídeo não permitido."
        }), 400

    nome_original = secure_filename(arquivo.filename)
    data = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    nome_final = data + "_" + nome_original
    caminho = os.path.join(PASTA_VIDEOS, nome_final)

    arquivo.save(caminho)

    return jsonify({
        "sucesso": True,
        "tipo": "video",
        "arquivo": nome_final
    })

@app.route("/uploads/fotos/<filename>")
def mostrar_foto(filename):
    return send_from_directory(PASTA_FOTOS, filename)

@app.route("/uploads/videos/<filename>")
def mostrar_video(filename):
    return send_from_directory(PASTA_VIDEOS, filename)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("admin_logado"):
        return redirect(url_for("painel_admin"))

    erro = None

    if request.method == "POST":
        senha = request.form.get("senha", "")

        if hmac.compare_digest(senha, ADMIN_PASSWORD):
            session["admin_logado"] = True
            return redirect(url_for("painel_admin"))

        erro = "Senha incorreta."

    return render_template("admin_login.html", erro=erro)

@app.route("/admin/painel")
def painel_admin():
    if not session.get("admin_logado"):
        return redirect(url_for("admin"))

    fotos = os.listdir(PASTA_FOTOS)
    videos = os.listdir(PASTA_VIDEOS)
    analises = carregar_analises()

    fotos.sort(reverse=True)
    videos.sort(reverse=True)

    return render_template(
        "admin.html",
        fotos=fotos,
        videos=videos,
        analises=analises
    )

@app.route("/admin/excluir/foto/<filename>", methods=["POST"])
def excluir_foto(filename):
    if not session.get("admin_logado"):
        return redirect(url_for("admin"))

    nome = os.path.basename(filename)
    caminho = os.path.join(PASTA_FOTOS, nome)

    if os.path.isfile(caminho):
        os.remove(caminho)

    analises = [
        item for item in carregar_analises()
        if item.get("arquivo") != nome
    ]

    salvar_analises(analises)

    return redirect(url_for("painel_admin"))

@app.route("/admin/excluir/video/<filename>", methods=["POST"])
def excluir_video(filename):
    if not session.get("admin_logado"):
        return redirect(url_for("admin"))

    nome = os.path.basename(filename)
    caminho = os.path.join(PASTA_VIDEOS, nome)

    if os.path.isfile(caminho):
        os.remove(caminho)

    return redirect(url_for("painel_admin"))

@app.route("/admin/excluir/analise/<analise_id>", methods=["POST"])
def excluir_analise(analise_id):
    if not session.get("admin_logado"):
        return redirect(url_for("admin"))

    analises = [
        item for item in carregar_analises()
        if item.get("id") != analise_id
    ]

    salvar_analises(analises)

    return redirect(url_for("painel_admin"))

@app.route("/admin/sair")
def sair_admin():
    session.pop("admin_logado", None)
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
