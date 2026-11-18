import re

import pymysql

from . import RegraNegocioError


def somente_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def cpf_valido(cpf):
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11 % 10
        if digito != int(cpf[tamanho]):
            return False
    return True


def cnpj_valido(cnpj):
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    for pesos in (pesos1, pesos2):
        soma = sum(int(d) * p for d, p in zip(cnpj, pesos))
        resto = soma % 11
        digito = 0 if resto < 2 else 11 - resto
        if digito != int(cnpj[len(pesos)]):
            return False
    return True


def formatar_cpf_cnpj(valor):
    if len(valor) == 11:
        return f"{valor[:3]}.{valor[3:6]}.{valor[6:9]}-{valor[9:]}"
    if len(valor) == 14:
        return f"{valor[:2]}.{valor[2:5]}.{valor[5:8]}/{valor[8:12]}-{valor[12:]}"
    return valor


def validar_cpf_cnpj(valor):
    """Regra 7: CPF ou CNPJ válido. Devolve apenas os dígitos."""
    digitos = somente_digitos(valor)
    if len(digitos) == 11:
        if not cpf_valido(digitos):
            raise RegraNegocioError("CPF inválido. Confira os números digitados.")
    elif len(digitos) == 14:
        if not cnpj_valido(digitos):
            raise RegraNegocioError("CNPJ inválido. Confira os números digitados.")
    else:
        raise RegraNegocioError("Informe um CPF (11 dígitos) ou um CNPJ (14 dígitos).")
    return digitos


def _validar(nome, cpf_cnpj, telefone, email):
    nome = (nome or "").strip()
    if not nome:
        raise RegraNegocioError("Informe o nome do interessado.")
    if len(nome) > 120:
        raise RegraNegocioError("O nome pode ter no máximo 120 caracteres.")
    digitos = validar_cpf_cnpj(cpf_cnpj)
    telefone = (telefone or "").strip() or None
    email = (email or "").strip() or None
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise RegraNegocioError("E-mail inválido.")
    return nome, digitos, telefone, email


def listar(db):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM interessado ORDER BY nome")
        return cur.fetchall()


def buscar(db, id_interessado):
    with db.cursor() as cur:
        cur.execute("SELECT * FROM interessado WHERE id_interessado = %s", (id_interessado,))
        return cur.fetchone()


def incluir(db, nome, cpf_cnpj, telefone=None, email=None):
    dados = _validar(nome, cpf_cnpj, telefone, email)
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO interessado (nome, cpf_cnpj, telefone, email) VALUES (%s, %s, %s, %s)", dados
            )
            novo_id = cur.lastrowid
        db.commit()
        return novo_id
    except pymysql.err.IntegrityError:
        db.rollback()
        raise RegraNegocioError("Já existe um interessado cadastrado com esse CPF ou CNPJ.")


def alterar(db, id_interessado, nome, cpf_cnpj, telefone=None, email=None):
    dados = _validar(nome, cpf_cnpj, telefone, email)
    try:
        with db.cursor() as cur:
            cur.execute(
                "UPDATE interessado SET nome = %s, cpf_cnpj = %s, telefone = %s, email = %s "
                "WHERE id_interessado = %s",
                (*dados, id_interessado),
            )
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        raise RegraNegocioError("Já existe um interessado cadastrado com esse CPF ou CNPJ.")


def excluir(db, id_interessado):
    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM interessado WHERE id_interessado = %s", (id_interessado,))
        db.commit()
    except pymysql.err.IntegrityError:
        db.rollback()
        raise RegraNegocioError("Este interessado não pode ser excluído porque tem documentos protocolados.")
