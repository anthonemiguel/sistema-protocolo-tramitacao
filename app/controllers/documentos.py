from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from ..db import get_db
from ..models import RegraNegocioError
from ..models import documento as documento_model
from ..models import interessado as interessado_model
from ..models import setor as setor_model
from ..models import tramitacao as tramitacao_model
from . import login_obrigatorio, usuario_logado

bp = Blueprint("documentos", __name__, url_prefix="/documentos")


@bp.route("/novo", methods=["GET", "POST"])
@login_obrigatorio
def novo():
    db = get_db()
    if request.method == "POST":
        try:
            id_documento, numero = documento_model.protocolar(
                db,
                request.form.get("tipo"),
                request.form.get("assunto"),
                request.form.get("id_interessado", type=int),
                usuario_logado(),
            )
            flash(f"Documento protocolado com o número {numero}.", "success")
            return redirect(url_for("documentos.detalhe", id_documento=id_documento))
        except RegraNegocioError as erro:
            flash(str(erro), "danger")
    return render_template(
        "documento_novo.html",
        tipos=documento_model.TIPOS,
        interessados=interessado_model.listar(db),
        form=request.form,
    )


@bp.route("/<int:id_documento>")
@login_obrigatorio
def detalhe(id_documento):
    db = get_db()
    documento = documento_model.buscar(db, id_documento)
    if documento is None:
        abort(404)
    usuario = usuario_logado()
    pode_agir = documento["situacao"] == documento_model.EM_TRAMITACAO and documento["id_setor_atual"] == usuario["id_setor"]
    return render_template(
        "documento_detalhe.html",
        documento=documento,
        historico=tramitacao_model.historico(db, id_documento),
        setores=[s for s in setor_model.listar(db) if s["id_setor"] != documento["id_setor_atual"]],
        pode_agir=pode_agir,
    )


@bp.route("/<int:id_documento>/tramitar", methods=["POST"])
@login_obrigatorio
def tramitar(id_documento):
    try:
        documento_model.tramitar(
            get_db(), id_documento, request.form.get("id_setor_destino"), request.form.get("despacho"), usuario_logado()
        )
        flash("Documento enviado ao setor de destino.", "success")
    except RegraNegocioError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("documentos.detalhe", id_documento=id_documento))


@bp.route("/<int:id_documento>/arquivar", methods=["POST"])
@login_obrigatorio
def arquivar(id_documento):
    try:
        documento_model.arquivar(get_db(), id_documento, usuario_logado())
        flash("Documento arquivado. A tramitação foi encerrada.", "success")
    except RegraNegocioError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("documentos.detalhe", id_documento=id_documento))
