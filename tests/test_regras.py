"""Testes das regras de negócio (item 3.3 do projeto)."""
import inspect
from datetime import datetime

import pytest

from app.models import RegraNegocioError
from app.models import documento, interessado, tramitacao
from conftest import SENHA


def _protocolar(db, dados, quando=None):
    return documento.protocolar(
        db, "Requerimento", "Assunto de teste", dados["id_interessado"], dados["usuarios"]["PROT"], quando
    )


def test_regra1_numero_no_formato_ano_sequencial(db, dados):
    quando = datetime(2026, 3, 10, 9, 0)
    _, primeiro = _protocolar(db, dados, quando)
    _, segundo = _protocolar(db, dados, quando)
    assert primeiro == "2026/00001"
    assert segundo == "2026/00002"


def test_regra1_sequencial_reinicia_a_cada_ano(db, dados):
    _protocolar(db, dados, datetime(2025, 12, 30, 10, 0))
    _, ultimo_2025 = _protocolar(db, dados, datetime(2025, 12, 31, 10, 0))
    _, primeiro_2026 = _protocolar(db, dados, datetime(2026, 1, 2, 10, 0))
    assert ultimo_2025 == "2025/00002"
    assert primeiro_2026 == "2026/00001"


def test_regra2_protocolo_cria_primeira_tramitacao(db, dados):
    id_doc, _ = _protocolar(db, dados)
    historico = tramitacao.historico(db, id_doc)
    assert len(historico) == 1
    assert historico[0]["id_setor_origem"] is None
    assert historico[0]["id_setor_destino"] == dados["setores"]["PROT"]
    assert documento.buscar(db, id_doc)["id_setor_atual"] == dados["setores"]["PROT"]


def test_regra3_so_o_setor_atual_pode_tramitar(db, dados):
    id_doc, _ = _protocolar(db, dados)
    outro_setor = dados["usuarios"]["SEFIN"]
    with pytest.raises(RegraNegocioError, match="Só o setor"):
        documento.tramitar(db, id_doc, dados["setores"]["SEOB"], "Tentativa indevida", outro_setor)
    assert len(tramitacao.historico(db, id_doc)) == 1


def test_regra4_destino_diferente_da_origem(db, dados):
    id_doc, _ = _protocolar(db, dados)
    with pytest.raises(RegraNegocioError, match="diferente"):
        documento.tramitar(db, id_doc, dados["setores"]["PROT"], "Para o próprio setor", dados["usuarios"]["PROT"])


def test_regra5_documento_arquivado_nao_tramita(db, dados):
    id_doc, _ = _protocolar(db, dados)
    documento.tramitar(db, id_doc, dados["setores"]["SEFIN"], "Para análise", dados["usuarios"]["PROT"])
    documento.arquivar(db, id_doc, dados["usuarios"]["SEFIN"])
    with pytest.raises(RegraNegocioError, match="arquivado"):
        documento.tramitar(db, id_doc, dados["setores"]["SEOB"], "Depois de arquivado", dados["usuarios"]["SEFIN"])
    doc = documento.buscar(db, id_doc)
    assert doc["situacao"] == "Arquivado"
    assert doc["id_setor_atual"] == dados["setores"]["SEFIN"]


def test_regra6_historico_sem_edicao_nem_exclusao(client):
    funcoes = [nome for nome, _ in inspect.getmembers(tramitacao, inspect.isfunction)]
    assert sorted(funcoes) == ["historico", "registrar"]
    rotas_tramitacao = [
        regra for regra in client.application.url_map.iter_rules() if "tramitacao" in regra.rule
    ]
    assert rotas_tramitacao == []


def test_regra7_cpf_cnpj_validado_e_unico(db, dados):
    with pytest.raises(RegraNegocioError, match="CPF inválido"):
        interessado.incluir(db, "Nome", "111.111.111-11")
    with pytest.raises(RegraNegocioError, match="CNPJ inválido"):
        interessado.incluir(db, "Empresa", "12.345.678/0001-00")
    with pytest.raises(RegraNegocioError, match="Já existe"):
        interessado.incluir(db, "Outra Pessoa", "52998224725")


def test_tela_tramitar_arquivado_mostra_mensagem_de_bloqueio(client, db, dados):
    id_doc, _ = _protocolar(db, dados)
    documento.arquivar(db, id_doc, dados["usuarios"]["PROT"])
    client.post("/login", data={"login": "user_prot", "senha": SENHA})
    resposta = client.post(
        f"/documentos/{id_doc}/tramitar",
        data={"id_setor_destino": dados["setores"]["SEFIN"], "despacho": "Teste"},
        follow_redirects=True,
    )
    assert "está arquivado e não pode ser tramitado" in resposta.get_data(as_text=True)


def test_painel_exige_login(client):
    resposta = client.get("/painel")
    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]
