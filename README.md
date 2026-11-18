# Sistema de Protocolo e Tramitação

Trabalho da disciplina Projeto Integrador Transdisciplinar em Sistemas de Informação II (Universidade Cruzeiro do Sul Virtual). Sistema web para protocolar documentos de um órgão público fictício (Prefeitura Municipal de Vila Serena), tramitá-los entre setores e manter o histórico completo.

- Sistema publicado: https://sistema-protocolo-tramitacao.onrender.com
- Tecnologias: Python 3, Flask, MySQL (PyMySQL), Bootstrap, pytest.

## Estrutura (padrão MVC)

```
app/models/        Model: acesso ao banco e regras de negócio
app/controllers/   Controller: rotas
app/templates/     View: páginas HTML
app/static/        CSS e JavaScript
database/          schema.sql (projeto físico) e seed.py (dados de demonstração)
tests/             testes automatizados (pytest)
docs/              diagramas, capturas, kit do testador, guia de publicação
```

## Como rodar no Windows

Pré-requisitos: Python 3.11 ou superior (python.org, marcar "Add python.exe to PATH") e MySQL Community Server 8 (dev.mysql.com/downloads/installer).

1. No MySQL Command Line Client (ou Workbench), como root:

```sql
CREATE DATABASE protocolo CHARACTER SET utf8mb4;
CREATE DATABASE protocolo_teste CHARACTER SET utf8mb4;
CREATE USER 'protocolo'@'localhost' IDENTIFIED BY 'escolha-uma-senha';
GRANT ALL ON protocolo.* TO 'protocolo'@'localhost';
GRANT ALL ON protocolo_teste.* TO 'protocolo'@'localhost';
```

2. No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.exemplo .env
notepad .env
```

3. No `.env`, preencha `DB_PASSWORD`, `SECRET_KEY`, `SENHA_AVALIADOR` e `SENHA_TESTADOR`. Depois:

```powershell
python database/seed.py
flask --app wsgi run
```

4. Abra http://127.0.0.1:5000 e entre com `avaliador` e a senha definida em `SENHA_AVALIADOR`.

Testes: `python -m pytest -v` (usam o banco `protocolo_teste`, recriado a cada teste).

## Publicação

Passo a passo em `docs/hospedagem.md` (Render para a aplicação e Aiven para o MySQL, planos gratuitos).

## Limitações desta versão

Sem recuperação de senha, cadastro de usuários pela tela, anexos, desarquivamento ou notificações. Os usuários são criados pelo `database/seed.py`.
