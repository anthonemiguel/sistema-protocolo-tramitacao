"""Prepara um banco MySQL de teste, recriado do zero a cada teste.

Usa as variáveis do .env, trocando o banco por TEST_DB_NAME
(padrão: protocolo_teste). Nunca roda contra o banco principal.
"""
import os
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(RAIZ / ".env")

from app import create_app  # noqa: E402
from app.db import conectar, config_do_ambiente  # noqa: E402
from app.models import interessado, usuario  # noqa: E402

SENHA = "senha-de-teste"


def _config_teste():
    cfg = config_do_ambiente()
    cfg["DB_NAME"] = os.environ.get("TEST_DB_NAME", "protocolo_teste")
    if cfg["DB_NAME"] == os.environ.get("DB_NAME"):
        pytest.exit("TEST_DB_NAME não pode ser igual a DB_NAME.")
    return cfg


def _recriar_schema(db):
    sql = (RAIZ / "database" / "schema.sql").read_text(encoding="utf-8")
    with db.cursor() as cur:
        for comando in sql.split(";"):
            linhas = [l for l in comando.splitlines() if not l.strip().startswith("--")]
            if "".join(linhas).strip():
                cur.execute("\n".join(linhas))
    db.commit()


@pytest.fixture
def db():
    conexao = conectar(_config_teste())
    _recriar_schema(conexao)
    yield conexao
    conexao.close()


@pytest.fixture
def dados(db):
    """Três setores (PROT recebe protocolos), um usuário em cada um e um interessado."""
    ids = {}
    with db.cursor() as cur:
        for nome, sigla, prot in [("Protocolo Geral", "PROT", 1), ("Finanças", "SEFIN", 0), ("Obras", "SEOB", 0)]:
            cur.execute("INSERT INTO setor (nome, sigla, eh_protocolo) VALUES (%s, %s, %s)", (nome, sigla, prot))
            ids[sigla] = cur.lastrowid
    db.commit()
    usuarios = {}
    for sigla in ids:
        login = f"user_{sigla.lower()}"
        id_usuario = usuario.incluir(db, f"Usuário {sigla}", login, SENHA, "administrador", ids[sigla])
        usuarios[sigla] = {"id_usuario": id_usuario, "id_setor": ids[sigla], "login": login}
    id_interessado = interessado.incluir(db, "Pessoa Fictícia", "529.982.247-25")
    return {"setores": ids, "usuarios": usuarios, "id_interessado": id_interessado}


@pytest.fixture
def client(db):
    app = create_app({**_config_teste(), "TESTING": True, "SECRET_KEY": "teste"})
    return app.test_client()
