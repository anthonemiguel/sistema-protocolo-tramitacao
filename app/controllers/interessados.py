from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..models import RegraNegocioError
from ..models import interessado as interessado_model
from . import admin_obrigatorio

bp = Blueprint("interessados", __name__, url_prefix="/interessados")


def _dados_do_form():
    f = request.form
    return f.get("nome"), f.get("cpf_cnpj"), f.get("telefone"), f.get("email")


@bp.route("/")
@admin_obrigatorio
def lista():
    return render_template("interessados/lista.html", interessados=interessado_model.listar(get_db()))


@bp.route("/novo", methods=["GET", "POST"])
@admin_obrigatorio
def novo():
    if request.method == "POST":
        try:
            interessado_model.incluir(get_db(), *_dados_do_form())
            flash("Interessado incluído.", "success")
            return redirect(url_for("interessados.lista"))
        except RegraNegocioError as erro:
            flash(str(erro), "danger")
    return render_template("interessados/form.html", interessado=request.form, titulo="Novo interessado")


@bp.route("/<int:id_interessado>/editar", methods=["GET", "POST"])
@admin_obrigatorio
def editar(id_interessado):
    db = get_db()
    interessado = interessado_model.buscar(db, id_interessado)
    if interessado is None:
        abort(404)
    if request.method == "POST":
        try:
            interessado_model.alterar(db, id_interessado, *_dados_do_form())
            flash("Interessado alterado.", "success")
            return redirect(url_for("interessados.lista"))
        except RegraNegocioError as erro:
            flash(str(erro), "danger")
            interessado = request.form
    return render_template("interessados/form.html", interessado=interessado, titulo="Editar interessado")


@bp.route("/<int:id_interessado>/excluir", methods=["POST"])
@admin_obrigatorio
def excluir(id_interessado):
    try:
        interessado_model.excluir(get_db(), id_interessado)
        flash("Interessado excluído.", "success")
    except RegraNegocioError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("interessados.lista"))
