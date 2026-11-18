"""Histórico de tramitação.

Regra 6: o histórico não pode ser editado nem excluído. Por isso este módulo
oferece apenas inclusão e consulta; não existe função de alteração ou exclusão,
e nenhuma rota do sistema altera a tabela tramitacao.
"""


def registrar(cur, id_documento, id_setor_origem, id_setor_destino, despacho, id_usuario, data_hora=None):
    """Inclui um registro usando o cursor da transação em andamento."""
    if data_hora is None:
        cur.execute(
            "INSERT INTO tramitacao (id_documento, id_setor_origem, id_setor_destino, despacho, id_usuario) "
            "VALUES (%s, %s, %s, %s, %s)",
            (id_documento, id_setor_origem, id_setor_destino, despacho, id_usuario),
        )
    else:
        cur.execute(
            "INSERT INTO tramitacao (id_documento, id_setor_origem, id_setor_destino, despacho, id_usuario, data_hora) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (id_documento, id_setor_origem, id_setor_destino, despacho, id_usuario, data_hora),
        )
    return cur.lastrowid


def historico(db, id_documento):
    with db.cursor() as cur:
        cur.execute(
            "SELECT t.*, so.sigla AS origem_sigla, so.nome AS origem_nome, "
            "sd.sigla AS destino_sigla, sd.nome AS destino_nome, u.nome AS usuario_nome "
            "FROM tramitacao t "
            "LEFT JOIN setor so ON so.id_setor = t.id_setor_origem "
            "JOIN setor sd ON sd.id_setor = t.id_setor_destino "
            "JOIN usuario u ON u.id_usuario = t.id_usuario "
            "WHERE t.id_documento = %s ORDER BY t.data_hora, t.id_tramitacao",
            (id_documento,),
        )
        return cur.fetchall()
