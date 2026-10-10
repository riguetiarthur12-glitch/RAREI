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
import json
import hmac
from datetime import datetime


app = Flask(__name__)

# =========================================================
# SEGURANÇA DO ADMIN
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
# PASTAS / ARQUIVOS
# =========================================================

PASTA_FOTOS = os.path.join("uploads", "fotos")
PASTA_VIDEOS = os.path.join("uploads", "videos")
PASTA_DADOS = "dados"
ARQUIVO_ANALISES = os.path.join(PASTA_DADOS, "analises.json")

os.makedirs(PASTA_FOTOS, exist_ok=True)
os.makedirs(PASTA_VIDEOS, exist_ok=True)
os.makedirs(PASTA_DADOS, exist_ok=True)


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

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
        json.dump(
            analises,
            arquivo,
            ensure_ascii=False,
            indent=2
        )

    os.replace(temp, ARQUIVO_ANALISES)


def nome_comum_pt(nome_modelo):
    # Pequeno mapa inicial. Podemos ampliar depois.
    traducoes = {
        "capybara": "Capivara",
        "lesser capybara": "Capivara-menor",
        "jaguar": "Onça-pintada",
        "puma": "Onça-parda",
        "ocelot": "Jaguatirica",
        "giant anteater": "Tamanduá-bandeira",
        "lowland tapir": "Anta",
        "nine-banded armadillo": "Tatu-galinha",
