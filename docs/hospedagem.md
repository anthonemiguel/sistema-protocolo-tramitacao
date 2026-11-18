# Publicação no PythonAnywhere (plano gratuito)

Nos comandos abaixo, troque `SEU_USUARIO` pelo seu nome de usuário do PythonAnywhere. O endereço final será `https://SEU_USUARIO.pythonanywhere.com`.

## Item 1. Conta

1. Crie a conta em https://www.pythonanywhere.com/registration/register/beginner/ (plano *Beginner*, gratuito).
2. Confirme o e-mail.

## Item 2. Banco MySQL

1. No menu superior, abra **Databases**.
2. Em *MySQL password*, defina uma senha para o banco e clique em **Set MySQL password**. Anote essa senha; ela vai para o `.env` no item 4.
3. Em *Create a database*, digite `protocolo` e clique em **Create**. O banco criado se chama `SEU_USUARIO$protocolo`.
4. Anote o *Database host address* mostrado na página (algo como `SEU_USUARIO.mysql.pythonanywhere-services.com`).

## Item 3. Código e bibliotecas

1. No menu superior, abra **Consoles** e clique em **Bash**.
2. No console, rode um comando por vez:

```bash
git clone https://github.com/anthonemiguel/sistema-protocolo-tramitacao.git
```

```bash
cd sistema-protocolo-tramitacao
```

```bash
mkvirtualenv --python=/usr/bin/python3.11 protocolo
```

```bash
pip install -r requirements.txt
```

## Item 4. Arquivo `.env` (senhas ficam só no servidor)

Ainda no console Bash, dentro da pasta `sistema-protocolo-tramitacao`:

```bash
cp .env.exemplo .env
```

```bash
nano .env
```

Preencha assim (os valores entre `<>` são seus):

```
DB_HOST=SEU_USUARIO.mysql.pythonanywhere-services.com
DB_PORT=3306
DB_USER=SEU_USUARIO
DB_PASSWORD=<senha do MySQL definida no item 2>
DB_NAME=SEU_USUARIO$protocolo
TEST_DB_NAME=SEU_USUARIO$protocolo_teste
SECRET_KEY=<um texto longo qualquer, por exemplo 40 letras e números misturados>
SENHA_AVALIADOR=<senha que será entregue ao avaliador>
SENHA_TESTADOR=<senha que será entregue aos testadores>
```

Para salvar no `nano`: Ctrl+O, Enter, Ctrl+X.

## Item 5. Carga dos dados de demonstração

```bash
python database/seed.py
```

A mensagem esperada é `Banco recriado: 5 setores, 9 interessados, 18 documentos.`

Atenção: este comando apaga e recria o banco. Depois que os testadores começarem, não rode de novo.

## Item 6. Aplicação web

1. No menu superior, abra **Web** e clique em **Add a new web app**.
2. Clique em **Next**, escolha **Manual configuration** (não escolha "Flask") e depois **Python 3.11**. Clique em **Next** até terminar.
3. Na seção **Virtualenv**, clique no campo e digite `protocolo`. Confirme.
4. Na seção **Code**, clique no link do *WSGI configuration file* (`/var/www/SEU_USUARIO_pythonanywhere_com_wsgi.py`). Apague todo o conteúdo e cole:

```python
import sys

caminho = "/home/SEU_USUARIO/sistema-protocolo-tramitacao"
if caminho not in sys.path:
    sys.path.insert(0, caminho)

from dotenv import load_dotenv
load_dotenv(caminho + "/.env")

from wsgi import app as application
```

5. Clique em **Save** e volte à aba **Web**.
6. Na seção **Static files**, adicione: URL `/static/` e Directory `/home/SEU_USUARIO/sistema-protocolo-tramitacao/app/static`.
7. Em **Security**, ative **Force HTTPS**.
8. Clique no botão verde **Reload SEU_USUARIO.pythonanywhere.com**.
9. Abra `https://SEU_USUARIO.pythonanywhere.com` e entre com `avaliador` e a senha escolhida.

Se aparecer erro, a aba **Web** tem o link **Error log**; copie as últimas linhas e me envie.

## Item 7. Atualizar depois de uma correção

```bash
cd ~/sistema-protocolo-tramitacao && git pull
```

Depois, na aba **Web**, clique em **Reload**.

## Item 8. Validade no plano gratuito

No plano gratuito, a aplicação fica no ar por três meses. Para renovar, entre na aba **Web** e clique em **Run until 3 months from today**. O PythonAnywhere avisa por e-mail antes de desligar. Confira a data mostrada nessa aba antes da correção do trabalho.
