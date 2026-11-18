import pymysql

from . import RegraNegocioError


def listar(db):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM setor ORDER BY nome")
        return cur.fetchall()


def buscar(db, id_setor):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM setor WHERE id_setor = %s", (id_setor,))
        return cur.fetchone()


def setor_de_protocolo(db):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM setor WHERE eh_protocolo = 1 ORDER BY id_setor LIMIT 1")
        return cur.fetchone()


def _validar(nome, sigla):
    nome = (nome or "").strip()
    sigla = (sigla or "").strip().upper()
    if not nome:
        raise RegraNegocioError("Informe o nome do setor.")
    if not sigla:
        raise RegraNegocioError("Informe a sigla do setor.")
    if len(nome) > 80:
        raise RegraNegocioError("O nome do setor pode ter no máximo 80 caracteres.")
    if len(sigla) > 10:
        raise RegraNegocioError("A sigla pode ter no máximo 10 caracteres.")
    return nome, sigla


def incluir(db, nome, sigla):
    nome, sigla = _validar(nome, sigla)
    try:
        with db.cursor() as cur:
            cur.execute("INSERT INTO setor (nome, sigla) VALUES (%s, %s)", (nome, sigla))
            novo_id = cur.lastrowid
        db.commit()
        return novo_id
    except pymysql.err.IntegrityError:
        db.rollback()
        raise RegraNegocioError("Já existe um setor com esse nome ou sigla.")


def alterar(db, id_setor, nome, sigla):
    nome, sigla = _validar(nome, sigla)
    try:
        with db.cursor() as cur:
            cur.execute("UPDATE setor SET nome = %s, sigla = %s WHERE id_setor = %s", (nome, sigla, id_setor))
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        raise RegraNegocioError("Já existe um setor com esse nome ou sigla.")


def excluir(db, id_setor):
    setor = buscar(db, id_setor)
    if setor is None:
        raise RegraNegocioError("Setor não encontrado.")
    if setor["eh_protocolo"]:
        raise RegraNegocioError("O setor de protocolo não pode ser excluído.")
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM setor WHERE id_setor = %s", (id_setor,))
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        raise RegraNegocioError(
            "Este setor não pode ser excluído porque tem usuários, documentos ou histórico ligados a ele."
        )
