"""Recria o banco e carrega os dados de demonstração (todos fictícios).

Uso: python database/seed.py            (apaga e recria tudo)
     python database/seed.py --se-vazio (só carrega se o banco ainda não tiver tabelas;
                                         usado na publicação para não apagar dados de teste)

Lê a conexão do arquivo .env. As senhas dos usuários de demonstração vêm das
variáveis SENHA_AVALIADOR e SENHA_TESTADOR, para não ficarem gravadas no
repositório. Os demais usuários recebem senha aleatória (não fazem login).

Os documentos são criados pelas mesmas funções da camada Model usadas pelo
sistema, então numeração e histórico seguem as regras de negócio.
"""
import os
import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from dotenv import load_dotenv  # noqa: E402

from app.db import conectar, config_do_ambiente  # noqa: E402
from app.models import documento, interessado, usuario  # noqa: E402


def executar_schema(db):
    sql = (RAIZ / "database" / "schema.sql").read_text(encoding="utf-8")
    comandos = [c.strip() for c in sql.split(";")]
    with db.cursor() as cur:
        for comando in comandos:
            linhas = [l for l in comando.splitlines() if not l.strip().startswith("--")]
            if "".join(linhas).strip():
                cur.execute("\n".join(linhas))
    db.commit()


def completar_cpf(base9):
    d = [int(c) for c in base9]
    for tamanho in (9, 10):
        soma = sum(d[i] * (tamanho + 1 - i) for i in range(tamanho))
        d.append((soma * 10) % 11 % 10)
    return "".join(map(str, d))


def completar_cnpj(base12):
    d = [int(c) for c in base12]
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for pesos in (pesos1, [6] + pesos1):
        resto = sum(x * p for x, p in zip(d, pesos)) % 11
        d.append(0 if resto < 2 else 11 - resto)
    return "".join(map(str, d))


SETORES = [
    ("Protocolo Geral", "PROT", 1),
    ("Secretaria de Administração", "SEMAD", 0),
    ("Secretaria de Finanças", "SEFIN", 0),
    ("Secretaria de Obras e Urbanismo", "SEOB", 0),
    ("Procuradoria Jurídica", "PROJUR", 0),
]

# Nomes e números inventados. Os CPFs e CNPJs têm dígitos verificadores
# válidos apenas para passar na validação; não pertencem a ninguém.
INTERESSADOS = [
    ("Marta Regina Albuquerque", completar_cpf("418236951"), "(92) 98111-2034", "marta.albuquerque@exemplo.com"),
    ("Joaquim Pereira Lobo", completar_cpf("527114830"), "(92) 98222-4410", "joaquim.lobo@exemplo.com"),
    ("Luciana Farias Teles", completar_cpf("613902447"), "(92) 99133-7801", None),
    ("Ricardo Moura Sampaio", completar_cpf("704551382"), None, "ricardo.sampaio@exemplo.com"),
    ("Helena Castro Viana", completar_cpf("835270164"), "(92) 98444-0912", "helena.viana@exemplo.com"),
    ("Construtora Rio Serena Ltda.", completar_cnpj("123456780001"), "(92) 3611-4400", "contato@rioserena.exemplo.com"),
    ("Associação de Moradores do Bairro Jardim das Flores", completar_cnpj("234567810001"), "(92) 3622-1180", None),
    ("Papelaria Ponto Certo ME", completar_cnpj("345678920001"), "(92) 3633-5521", "vendas@pontocerto.exemplo.com"),
    ("Antônio Carlos Bezerra", completar_cpf("946318205"), "(92) 99255-6678", None),
]


def main():
    load_dotenv(RAIZ / ".env")
    senha_avaliador = os.environ.get("SENHA_AVALIADOR")
    senha_testador = os.environ.get("SENHA_TESTADOR")
    if not senha_avaliador or not senha_testador:
        sys.exit("Defina SENHA_AVALIADOR e SENHA_TESTADOR no arquivo .env antes de rodar o seed.")

    db = conectar(config_do_ambiente())
    if "--se-vazio" in sys.argv:
        with db.cursor() as cur:
            cur.execute("SHOW TABLES LIKE 'documento'")
            if cur.fetchone():
                print("Banco já carregado; nada foi alterado.")
                db.close()
                return
    executar_schema(db)

    ids_setor = {}
    with db.cursor() as cur:
        for nome, sigla, eh_protocolo in SETORES:
            cur.execute("INSERT INTO setor (nome, sigla, eh_protocolo) VALUES (%s, %s, %s)", (nome, sigla, eh_protocolo))
            ids_setor[sigla] = cur.lastrowid
    db.commit()

    def senha_aleatoria():
        return secrets.token_urlsafe(16)

    usuarios = {}
    for login, nome, senha, perfil, sigla in [
        ("avaliador", "Avaliador do Projeto", senha_avaliador, "administrador", "PROT"),
        ("testador", "Usuário de Teste", senha_testador, "administrador", "PROT"),
        ("cmonteiro", "Clara Monteiro", senha_aleatoria(), "servidor", "PROT"),
        ("pnogueira", "Paulo Nogueira", senha_aleatoria(), "servidor", "SEMAD"),
        ("fbrandao", "Fernanda Brandão", senha_aleatoria(), "servidor", "SEFIN"),
        ("rtavares", "Rogério Tavares", senha_aleatoria(), "servidor", "SEOB"),
        ("isoares", "Isabela Soares", senha_aleatoria(), "servidor", "PROJUR"),
    ]:
        id_usuario = usuario.incluir(db, nome, login, senha, perfil, ids_setor[sigla])
        usuarios[sigla if login not in ("avaliador", "testador") else login] = {
            "id_usuario": id_usuario,
            "id_setor": ids_setor[sigla],
        }

    ids_interessado = [interessado.incluir(db, *dados) for dados in INTERESSADOS]

    # (data do protocolo, tipo, assunto, índice do interessado, caminho, arquivar)
    # caminho: lista de (sigla de destino, despacho); cada passo ocorre um dia depois do anterior.
    documentos = [
        ("2025-11-10 09:12", "Requerimento", "Pedido de certidão negativa de débitos municipais", 0,
         [("SEFIN", "Encaminho para emissão da certidão.")], True),
        ("2025-11-18 14:30", "Ofício", "Solicitação de reparo na iluminação da Rua das Acácias", 6,
         [("SEOB", "Para vistoria e providências.")], True),
        ("2025-12-02 10:05", "Requerimento", "Pedido de alvará de construção residencial", 3,
         [("SEOB", "Para análise do projeto."), ("PROJUR", "Solicito parecer sobre recuo frontal."),
          ("SEOB", "Parecer favorável anexado.")], True),
        ("2025-12-15 11:40", "Memorando", "Proposta de atualização do regimento interno", 1,
         [("SEMAD", "Para análise da Secretaria de Administração.")], False),
        ("2026-01-08 08:50", "Requerimento", "Revisão do valor venal do imóvel para cálculo do IPTU", 4,
         [("SEFIN", "Para análise do cadastro imobiliário.")], False),
        ("2026-01-21 15:20", "Ofício", "Proposta comercial para fornecimento de material de expediente", 7,
         [("SEMAD", "Para conhecimento do setor de compras."), ("SEFIN", "Verificar disponibilidade orçamentária.")], False),
        ("2026-02-03 09:00", "Denúncia", "Descarte irregular de entulho em terreno baldio", 2,
         [("SEOB", "Para fiscalização no local.")], True),
        ("2026-02-17 13:45", "Requerimento", "Licença para evento comunitário na praça central", 6,
         [("SEMAD", "Para análise da documentação."), ("PROJUR", "Solicito parecer sobre responsabilidade civil.")], False),
        ("2026-03-05 10:30", "Ofício", "Medição da segunda etapa da obra de pavimentação", 5,
         [("SEOB", "Para conferência da medição."), ("SEFIN", "Medição conferida, encaminho para pagamento.")], False),
        ("2026-03-19 16:10", "Requerimento", "Pedido de parcelamento de débito de ISS", 7,
         [("SEFIN", "Para cálculo do parcelamento.")], True),
        ("2026-04-07 08:35", "Requerimento", "Segunda via de guia de IPTU", 8, [], False),
        ("2026-05-12 11:15", "Memorando", "Solicitação de cessão de servidor", 1,
         [("SEMAD", "Para análise do setor de pessoal."), ("PROJUR", "Avaliar legalidade da cessão.")], True),
        ("2026-06-23 14:00", "Requerimento", "Pedido de poda de árvore em via pública", 0,
         [("SEOB", "Para avaliação técnica.")], False),
        ("2026-08-04 09:40", "Ofício", "Pedido de informações sobre contrato de coleta de lixo", 6,
         [("PROJUR", "Para manifestação sobre o pedido de acesso à informação.")], False),
        ("2026-09-15 10:20", "Requerimento", "Restituição de taxa paga em duplicidade", 3, [], False),
        ("2026-10-27 15:55", "Outro", "Sugestão de melhoria no atendimento ao público", 4,
         [("SEMAD", "Para conhecimento.")], False),
        ("2026-11-09 09:05", "Requerimento", "Inscrição em programa de regularização fundiária", 2, [], False),
        ("2026-11-16 13:25", "Ofício", "Convite para audiência pública sobre o plano diretor", 5,
         [("SEMAD", "Para ciência e agenda do secretário.")], False),
    ]

    protocolista = {"id_usuario": usuarios["PROT"]["id_usuario"], "id_setor": ids_setor["PROT"]}
    for data_txt, tipo, assunto, idx, caminho, arquivar in documentos:
        momento = datetime.strptime(data_txt, "%Y-%m-%d %H:%M")
        id_doc, _numero = documento.protocolar(db, tipo, assunto, ids_interessado[idx], protocolista, momento)
        atual = "PROT"
        for destino, despacho in caminho:
            momento += timedelta(days=1, hours=2)
            documento.tramitar(db, id_doc, ids_setor[destino], despacho, usuarios[atual], momento)
            atual = destino
        if arquivar:
            momento += timedelta(days=2)
            documento.arquivar(db, id_doc, usuarios[atual], momento)

    db.close()
    print(f"Banco recriado: {len(SETORES)} setores, {len(INTERESSADOS)} interessados, {len(documentos)} documentos.")


if __name__ == "__main__":
    main()
