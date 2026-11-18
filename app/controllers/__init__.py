"""Camada Controller: rotas que recebem a requisição, chamam o Model e escolhem a View."""
from functools import wraps

from flask import flash, g, redirect, session, url_for

from ..db import get_db
from ..models import usuario as usuario_model


def usuario_logado():
    if "usuario" not in g:
        id_usuario = session.get("id_usuario")
        g.usuario = usuario_model.buscar(get_db(), id_usuario) if id_usuario else None
    return g.usuario


def login_obrigatorio(view):
    @wraps(view)
    def envolvida(*args, **kwargs):
        if usuario_logado() is None:
            flash("Entre com seu usuário e senha para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return envolvida


def admin_obrigatorio(view):
    @wraps(view)
    @login_obrigatorio
    def envolvida(*args, **kwargs):
        if usuario_logado()["perfil"] != "administrador":
            flash("Apenas administradores podem acessar os cadastros.", "danger")
            return redirect(url_for("painel.inicio"))
        return view(*args, **kwargs)

    return envolvida
