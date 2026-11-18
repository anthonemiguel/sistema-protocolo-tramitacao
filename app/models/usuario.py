from werkzeug.security import check_password_hash, generate_password_hash


def buscar(db, id_usuario):
    with db.cursor() as cur:
        cur.execute(
            "SELECT u.id_usuario, u.nome, u.login, u.perfil, u.id_setor, s.nome AS setor_nome, s.sigla AS setor_sigla "
            "FROM usuario u JOIN setor s ON s.id_setor = u.id_setor WHERE u.id_usuario = %s",
            (id_usuario,),
        )
        return cur.fetchone()


def autenticar(db, login, senha):
    """Devolve o usuário se login e senha conferem; caso contrário, None."""
    with db.cursor() as cur:
        cur.execute("SELECT id_usuario, senha_hash FROM usuario WHERE login = %s", ((login or "").strip(),))
        linha = cur.fetchone()
    if linha and check_password_hash(linha["senha_hash"], senha or ""):
        return buscar(db, linha["id_usuario"])
    return None


def incluir(db, nome, login, senha, perfil, id_setor):
    with db.cursor() as cur:
        cur.execute(
            "INSERT INTO usuario (nome, login, senha_hash, perfil, id_setor) VALUES (%s, %s, %s, %s, %s)",
            (nome, login, generate_password_hash(senha), perfil, id_setor),
        )
        novo_id = cur.lastrowid
    db.commit()
    return novo_id
