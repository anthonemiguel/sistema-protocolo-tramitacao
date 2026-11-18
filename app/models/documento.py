import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pymysql

from . import RegraNegocioError
from . import interessado as interessado_model
from . import setor as setor_model
from . import tramitacao as tramitacao_model

TIPOS = ["Requerimento", "Ofício", "Memorando", "Denúncia", "Outro"]
EM_TRAMITACAO = "Em tramitação"
ARQUIVADO = "Arquivado"

_SELECT = (
    "SELECT d.*, i.nome AS interessado_nome, i.cpf_cnpj, s.nome AS setor_nome, s.sigla AS setor_sigla "
    "FROM documento d "
    "JOIN interessado i ON i.id_interessado = d.id_interessado "
    "JOIN setor s ON s.id_setor = d.id_setor_atual "
)


def agora():
    """Data e hora local do órgão. O servidor e o banco na nuvem usam UTC."""
    fuso = ZoneInfo(os.environ.get("FUSO_HORARIO", "America/Manaus"))
    return datetime.now(fuso).replace(tzinfo=None, microsecond=0)


def formatar_numero(ano, sequencial):
    return f"{ano}/{sequencial:05d}"


def proximo_sequencial(cur, ano):
    """Regra 1: o sequencial reinicia a cada ano.

    O SELECT ... FOR UPDATE bloqueia as linhas do ano dentro da transação, para
    que dois protocolos simultâneos não recebam o mesmo número.
    """
    cur.execute("SELECT MAX(sequencial) AS ultimo FROM documento WHERE ano = %s FOR UPDATE", (ano,))
    ultimo = cur.fetchone()["ultimo"] or 0
    if ultimo >= 99999:
        raise RegraNegocioError(f"Limite de protocolos do ano {ano} atingido.")
    return ultimo + 1


def protocolar(db, tipo, assunto, id_interessado, usuario, data_hora=None):
    """Cria o documento com número automático e a primeira tramitação (regras 1 e 2)."""
    assunto = (assunto or "").strip()
    if tipo not in TIPOS:
        raise RegraNegocioError("Escolha um tipo de documento válido.")
    if not assunto:
        raise RegraNegocioError("Informe o assunto do documento.")
    if len(assunto) > 200:
        raise RegraNegocioError("O assunto pode ter no máximo 200 caracteres.")
    if not id_interessado or interessado_model.buscar(db, id_interessado) is None:
        raise RegraNegocioError("Escolha o interessado.")
    setor_protocolo = setor_model.setor_de_protocolo(db)
    if setor_protocolo is None:
        raise RegraNegocioError("Não há setor de protocolo cadastrado.")

    data_hora = data_hora or agora()
    ano = data_hora.year
    try:
        with db.cursor() as cur:
            sequencial = proximo_sequencial(cur, ano)
            numero = formatar_numero(ano, sequencial)
            cur.execute(
                "INSERT INTO documento (numero_protocolo, ano, sequencial, tipo, assunto, data_protocolo, "
                "id_interessado, id_setor_atual) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (numero, ano, sequencial, tipo, assunto, data_hora, id_interessado, setor_protocolo["id_setor"]),
            )
            id_documento = cur.lastrowid
            tramitacao_model.registrar(
                cur,
                id_documento,
                None,
                setor_protocolo["id_setor"],
                "Entrada do documento no setor de protocolo.",
                usuario["id_usuario"],
                data_hora,
            )
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        raise RegraNegocioError("Não foi possível gerar o número de protocolo. Tente novamente.")
    except Exception:
        db.rollback()
        raise
    return id_documento, numero


def buscar(db, id_documento):
    with db.cursor() as cur:
        cur.execute(_SELECT + "WHERE d.id_documento = %s", (id_documento,))
        return cur.fetchone()


def listar_do_setor(db, id_setor):
    with db.cursor() as cur:
        cur.execute(_SELECT + "WHERE d.id_setor_atual = %s ORDER BY d.situacao DESC, d.data_protocolo DESC", (id_setor,))
        return cur.fetchall()


def consultar(db, numero=None, termo_interessado=None):
    numero = (numero or "").strip()
    termo = (termo_interessado or "").strip()
    if numero:
        with db.cursor() as cur:
            cur.execute(_SELECT + "WHERE d.numero_protocolo LIKE %s ORDER BY d.data_protocolo DESC", (f"%{numero}%",))
            return cur.fetchall()
    if termo:
        digitos = interessado_model.somente_digitos(termo)
        with db.cursor() as cur:
            if digitos and len(digitos) >= 3 and digitos == termo.replace(".", "").replace("-", "").replace("/", ""):
                cur.execute(_SELECT + "WHERE i.cpf_cnpj LIKE %s ORDER BY d.data_protocolo DESC", (f"%{digitos}%",))
            else:
                cur.execute(_SELECT + "WHERE i.nome LIKE %s ORDER BY d.data_protocolo DESC", (f"%{termo}%",))
            return cur.fetchall()
    return []


def _verificar_setor_atual(documento, usuario):
    if documento is None:
        raise RegraNegocioError("Documento não encontrado.")
    if documento["situacao"] == ARQUIVADO:
        raise RegraNegocioError("Este documento está arquivado e não pode ser tramitado.")
    if documento["id_setor_atual"] != usuario["id_setor"]:
        raise RegraNegocioError(
            f"Só o setor onde o documento está ({documento['setor_sigla']}) pode tramitá-lo ou arquivá-lo."
        )


def tramitar(db, id_documento, id_setor_destino, despacho, usuario, data_hora=None):
    """Envia o documento a outro setor (regras 3, 4 e 5)."""
    documento = buscar(db, id_documento)
    _verificar_setor_atual(documento, usuario)
    despacho = (despacho or "").strip()
    try:
        id_setor_destino = int(id_setor_destino)
    except (TypeError, ValueError):
        raise RegraNegocioError("Escolha o setor de destino.")
    if setor_model.buscar(db, id_setor_destino) is None:
        raise RegraNegocioError("Setor de destino não encontrado.")
    if id_setor_destino == documento["id_setor_atual"]:
        raise RegraNegocioError("O setor de destino deve ser diferente do setor atual.")
    if not despacho:
        raise RegraNegocioError("Escreva o despacho (motivo do envio).")
    if len(despacho) > 500:
        raise RegraNegocioError("O despacho pode ter no máximo 500 caracteres.")
    data_hora = data_hora or agora()
    try:
        with db.cursor() as cur:
            tramitacao_model.registrar(
                cur, id_documento, documento["id_setor_atual"], id_setor_destino, despacho, usuario["id_usuario"], data_hora
            )
            cur.execute("UPDATE documento SET id_setor_atual = %s WHERE id_documento = %s", (id_setor_destino, id_documento))
        db.commit()
    except Exception:
        db.rollback()
        raise


def arquivar(db, id_documento, usuario, data_hora=None):
    """Encerra a tramitação. Só o setor onde o documento está pode arquivá-lo."""
    documento = buscar(db, id_documento)
    if documento is not None and documento["situacao"] == ARQUIVADO:
        raise RegraNegocioError("Este documento já está arquivado.")
    _verificar_setor_atual(documento, usuario)
    data_hora = data_hora or agora()
    with db.cursor() as cur:
        cur.execute(
            "UPDATE documento SET situacao = %s, data_arquivamento = %s WHERE id_documento = %s",
            (ARQUIVADO, data_hora, id_documento),
        )
    db.commit()
