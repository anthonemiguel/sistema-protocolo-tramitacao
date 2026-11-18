"""Conexão com o MySQL. Os dados de acesso vêm de variáveis de ambiente."""
import os

import pymysql
import pymysql.cursors
from flask import current_app, g


def conectar(config=None):
    cfg = config or current_app.config
    return pymysql.connect(
        host=cfg["DB_HOST"],
        port=int(cfg["DB_PORT"]),
        user=cfg["DB_USER"],
        password=cfg["DB_PASSWORD"],
        database=cfg["DB_NAME"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def get_db():
    if "db" not in g:
        g.db = conectar()
    return g.db


def fechar_db(_erro=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def config_do_ambiente():
    return {
        "DB_HOST": os.environ.get("DB_HOST", "localhost"),
        "DB_PORT": os.environ.get("DB_PORT", "3306"),
        "DB_USER": os.environ.get("DB_USER", ""),
        "DB_PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "DB_NAME": os.environ.get("DB_NAME", "protocolo"),
    }
