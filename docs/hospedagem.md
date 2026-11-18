# Publicação gratuita: Render (aplicação) e Aiven (banco MySQL)

O plano gratuito do PythonAnywhere não oferece mais MySQL e bloqueia conexão com bancos externos. Por isso a aplicação roda no Render e o banco MySQL no Aiven, ambos gratuitos. As senhas ficam só nesses dois serviços, nunca no GitHub.

## Item 1. Banco MySQL no Aiven

1. Acesse https://console.aiven.io/signup e crie a conta (pode entrar com o Google).
2. Se pedir para criar um projeto, aceite o nome sugerido.
3. Clique em **Create service**, escolha **MySQL**.
4. Em *Service tier*, escolha **Free**. Mantenha a região sugerida e clique em **Create free service**.
5. Espere a situação mudar de *Rebuilding* para **Running** (de 3 a 5 minutos).
6. Na página do serviço (*Overview*), em **Connection information**, deixe aberta esta aba. Você vai copiar daqui: **Host**, **Port**, **User**, **Password** (clique no ícone do olho) e **Database name** (normalmente `defaultdb`).
7. Na mesma área, em **CA certificate**, clique em **Download**. Abra o arquivo `ca.pem` baixado com o Bloco de Notas; o conteúdo será colado no item 2.

## Item 2. Aplicação no Render

1. Acesse https://dashboard.render.com/register e entre com a conta do GitHub (**GitHub**).
2. Clique em **New** e depois em **Web Service**.
3. Escolha **Git Provider**, autorize o Render no GitHub e selecione o repositório `sistema-protocolo-tramitacao`.
4. Preencha:
   - **Name**: `sistema-protocolo-tramitacao` (vira parte do endereço);
   - **Language**: `Python 3`;
   - **Branch**: `main`;
   - **Build Command**: `pip install -r requirements.txt && python database/seed.py --se-vazio`
   - **Start Command**: `gunicorn wsgi:app`
   - **Instance Type**: **Free**.
5. Em **Environment Variables**, clique em **Add Environment Variable** para cada linha abaixo:

| Nome | Valor |
|---|---|
| DB_HOST | Host do Aiven |
| DB_PORT | Port do Aiven |
| DB_USER | User do Aiven (normalmente `avnadmin`) |
| DB_PASSWORD | Password do Aiven |
| DB_NAME | Database name do Aiven (normalmente `defaultdb`) |
| DB_SSL_CA | `/etc/secrets/ca.pem` |
| SECRET_KEY | clique em **Generate** |
| SENHA_AVALIADOR | senha que você escolher para o avaliador |
| SENHA_TESTADOR | senha que você escolher para os testadores |

6. Ainda nessa área, em **Secret Files**, clique em **Add Secret File**: em *Filename* digite `ca.pem`; em *Contents* cole todo o texto do `ca.pem` aberto no Bloco de Notas (incluindo as linhas `-----BEGIN CERTIFICATE-----` e `-----END CERTIFICATE-----`).
7. Clique em **Deploy Web Service**.
8. Acompanhe o log. Durante a construção deve aparecer `Banco recriado: 5 setores, 9 interessados, 18 documentos.` No fim aparece `Your service is live`.
9. O endereço fica no alto da página, no formato `https://sistema-protocolo-tramitacao.onrender.com`. Abra e entre com `avaliador` e a senha escolhida.

Se a publicação falhar, copie as últimas 20 linhas do log e envie.

## Item 3. Atualizar depois de uma correção

Cada envio ao GitHub na branch `main` dispara uma nova publicação automática. A carga de dados não se repete: o comando `seed.py --se-vazio` só carrega quando o banco está vazio, então os registros feitos pelos testadores são mantidos.

Para recriar os dados de demonstração do zero (apaga tudo), troque temporariamente o Build Command para `pip install -r requirements.txt && python database/seed.py` e clique em **Manual Deploy**. Depois volte o comando ao original.

## Item 4. Limitações do plano gratuito

- O Render desliga a aplicação após 15 minutos sem acesso. O próximo acesso leva cerca de um minuto para carregar; depois disso fica normal. Esse aviso consta no kit do testador.
- O Aiven pode desligar serviços gratuitos parados por muito tempo, e avisa por e-mail antes. Antes da data da correção, abra o sistema uma vez e confira, no painel do Aiven, se o serviço está **Running**. Se estiver desligado, clique em **Power on**.
