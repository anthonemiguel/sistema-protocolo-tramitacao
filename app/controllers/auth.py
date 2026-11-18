from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..db import get_db
from ..models import usuario as usuario_model
from . import usuario_logado

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = usuario_model.autenticar(get_db(), request.form.get("login"), request.form.get("senha"))
        if usuario:
            session.clear()
            session["id_usuario"] = usuario["id_usuario"]
            flash(f"Bem-vindo(a), {usuario['nome']}.", "success")
            return redirect(url_for("painel.inicio"))
        flash("Usuário ou senha incorretos.", "danger")
    elif usuario_logado():
        return redirect(url_for("painel.inicio"))
    return render_template("login.html")


@bp.route("/sair")
def sair():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))
