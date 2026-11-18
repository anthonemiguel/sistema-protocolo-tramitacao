from flask import Blueprint, redirect, render_template, url_for

from ..db import get_db
from ..models import documento as documento_model
from . import login_obrigatorio, usuario_logado

bp = Blueprint("painel", __name__)


@bp.route("/")
def raiz():
    return redirect(url_for("painel.inicio"))


@bp.route("/painel")
@login_obrigatorio
def inicio():
    usuario = usuario_logado()
    documentos = documento_model.listar_do_setor(get_db(), usuario["id_setor"])
    return render_template("painel.html", documentos=documentos)
