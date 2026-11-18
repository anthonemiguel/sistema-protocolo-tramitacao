from flask import Blueprint, render_template, request

from ..db import get_db
from ..models import documento as documento_model
from . import login_obrigatorio

bp = Blueprint("consulta", __name__)


@bp.route("/consulta")
@login_obrigatorio
def consultar():
    numero = request.args.get("numero", "")
    interessado = request.args.get("interessado", "")
    pesquisou = bool(numero.strip() or interessado.strip())
    resultados = documento_model.consultar(get_db(), numero, interessado) if pesquisou else []
    return render_template(
        "consulta.html", resultados=resultados, numero=numero, interessado=interessado, pesquisou=pesquisou
    )
