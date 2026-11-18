from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..models import RegraNegocioError
from ..models import setor as setor_model
from . import admin_obrigatorio

bp = Blueprint("setores", __name__, url_prefix="/setores")


@bp.route("/")
@admin_obrigatorio
def lista():
    return render_template("setores/lista.html", setores=setor_model.listar(get_db()))


@bp.route("/novo", methods=["GET", "POST"])
@admin_obrigatorio
def novo():
    if request.method == "POST":
        try:
            setor_model.incluir(get_db(), request.form.get("nome"), request.form.get("sigla"))
            flash("Setor incluído.", "success")
            return redirect(url_for("setores.lista"))
        except RegraNegocioError as erro:
            flash(str(erro), "danger")
    return render_template("setores/form.html", setor=request.form, titulo="Novo setor")


@bp.route("/<int:id_setor>/editar", methods=["GET", "POST"])
@admin_obrigatorio
def editar(id_setor):
    db = get_db()
    setor = setor_model.buscar(db, id_setor)
    if setor is None:
        abort(404)
    if request.method == "POST":
        try:
            setor_model.alterar(db, id_setor, request.form.get("nome"), request.form.get("sigla"))
            flash("Setor alterado.", "success")
            return redirect(url_for("setores.lista"))
        except RegraNegocioError as erro:
            flash(str(erro), "danger")
            setor = request.form
    return render_template("setores/form.html", setor=setor, titulo="Editar setor")


@bp.route("/<int:id_setor>/excluir", methods=["POST"])
@admin_obrigatorio
def excluir(id_setor):
    try:
        setor_model.excluir(get_db(), id_setor)
        flash("Setor excluído.", "success")
    except RegraNegocioError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("setores.lista"))
