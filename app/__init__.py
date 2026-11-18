import os

from dotenv import load_dotenv
from flask import Flask

from .db import config_do_ambiente, fechar_db
from .models.interessado import formatar_cpf_cnpj

NOME_ORGAO = "Prefeitura Municipal de Vila Serena"


def create_app(config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.update(config_do_ambiente())
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(32)
    if config:
        app.config.update(config)

    app.teardown_appcontext(fechar_db)
    app.jinja_env.filters["cpf_cnpj"] = formatar_cpf_cnpj
    app.jinja_env.filters["data_hora"] = lambda d: d.strftime("%d/%m/%Y %H:%M") if d else ""
    app.jinja_env.filters["data"] = lambda d: d.strftime("%d/%m/%Y") if d else ""

    @app.context_processor
    def dados_globais():
        return {"NOME_ORGAO": NOME_ORGAO}

    from .controllers import auth, consulta, documentos, interessados, painel, setores

    for modulo in (auth, painel, documentos, consulta, setores, interessados):
        app.register_blueprint(modulo.bp)

    return app
