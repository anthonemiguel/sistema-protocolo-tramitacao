# Decisões do projeto

Registro das decisões do projeto. Trabalho da disciplina Projeto Integrador Transdisciplinar em Sistemas de Informação II (Cruzeiro do Sul Virtual). As decisões abaixo estão fechadas; não rediscutir. Impedimento técnico real: apontar e propor a alternativa mais próxima.

## Referências

- `referencia/PITSInformacaoII.md`: roteiro da disciplina.
- `referencia/PIT_atividade.docx`: template oficial de entrega (é o que será avaliado; preservar estrutura e formatação).
- `referencia/pit1/`: documentação do PIT-I, se fornecida.

## Forma de trabalho

- Fases do item 9 (tabela abaixo). Ao fim de cada fase: parar, resumir com caminhos dos arquivos, aguardar "aprovado". Nunca avançar duas fases.
- Ao fim de cada fase, informar o que do roteiro ou do template ficou sem atendimento.
- Escopo enxuto: nada de funcionalidades, telas ou seções extras sem consulta.
- Commits em português, curtos e descritivos, um por funcionalidade.

## Integridade (inegociável)

- Nunca inventar conteúdo de testes de terceiros. As cinco tabelas de testadores só são preenchidas com respostas reais em `testes/respostas/`. Sem resposta: marcação de pendência, nunca texto simulado.
- Transcrição: pode padronizar ortografia e pontuação; não pode alterar, acrescentar nem omitir conteúdo.
- Nunca gravar senhas, chaves ou dados de conexão no repositório. Usar variáveis de ambiente e `.env` (ignorado pelo Git). Modelo versionado: `.env.exemplo`.

## Sistema

Protocolo e tramitação de documentos de um órgão público fictício. Documento é protocolado, recebe número, circula entre setores, todo o caminho fica registrado.

Banco MySQL, cinco tabelas:

| Tabela | Conteúdo | Relacionamentos |
|---|---|---|
| setor | nome, sigla | tem vários usuários e documentos |
| usuario | nome, login, senha (hash), perfil | pertence a um setor |
| interessado | nome, CPF ou CNPJ, telefone, e-mail | tem vários documentos |
| documento | número de protocolo, tipo, assunto, data de protocolo, situação, setor atual | pertence a interessado, está em um setor |
| tramitacao | setor origem, setor destino, data e hora, despacho, usuário responsável | liga documento, setores e usuário |

Restrições expressam regras de negócio (NOT NULL, UNIQUE, CHECK, FK, DEFAULT). Ajustes de atributos permitidos na fase 2 se justificados.

Regras de negócio (ficam na camada Model, não nas rotas nem no banco):

1. Protocolo automático `AAAA/NNNNN` (ex.: 2026/00001), reinicia a cada ano, sem duplicidade.
2. Protocolar cria automaticamente a primeira tramitação (entrada no setor de protocolo).
3. Só o setor onde o documento está pode tramitá-lo.
4. Destino diferente da origem.
5. Documento arquivado não pode ser tramitado.
6. Histórico de tramitação não pode ser editado nem excluído.
7. CPF ou CNPJ do interessado validado e único.

Telas: login; painel com documentos do setor do usuário; protocolar; detalhe com histórico e ações de tramitar e arquivar; consulta por protocolo ou interessado; cadastros de setores e interessados (CRUD com confirmação antes de excluir). Toda ação dá retorno em linguagem simples. Interface em pt-BR.

Dados de demonstração: 4 a 5 setores, 8 a 10 interessados, 15 a 20 documentos em situações variadas com históricos coerentes, nenhum dado real. Um usuário para o avaliador e outro para os testadores.

## Pilha e arquitetura

Python + Flask; MySQL com PyMySQL; Bootstrap via CDN; pytest; Git e GitHub (público); PythonAnywhere (gratuito). Só bibliotecas necessárias, todas em `requirements.txt`.

MVC visível: `app/models` (banco e regras), `app/controllers` (rotas), `app/templates` (views), `app/static`; `database/schema.sql`, `database/seed.sql`; `tests/`; `docs/`; `README.md`. Rodar localmente com poucos comandos documentados no README; testes finais contra MySQL antes de publicar.

## Redação (todos os textos)

- Evitar: adjetivos vazios (robusto, intuitivo, eficiente, moderno, inovador); aberturas e fechamentos genéricos; travessões (usar vírgulas ou parênteses); trincas por hábito; negrito em excesso; conectivos em cadeia (além disso, dessa forma, nesse sentido); conclusões repetitivas; promessas que o sistema não cumpre.
- Preferir: frases curtas; referências concretas ao sistema (tela, número de protocolo, setor); registro honesto de limitações; redação impessoal.
- Cada seção: um a três parágrafos curtos. Volume nas tabelas, diagramas e capturas.
- Numeração: algarismos arábicos com o rótulo "item" (item 5, item 5.2, item 5.2.3); nunca número solto nem romano. Instituições, cursos e períodos por extenso.

## Substituição dos vídeos

Não haverá vídeos. O documento deve ser autossuficiente.

- Guia de avaliação no início: tabela exigência do roteiro → onde está comprovada (documento ou repositório).
- Seção "Demonstração da solução": um bloco por fluxo (objetivo em uma frase; passos numerados com uma captura por passo; resultado; regra evidenciada). Fluxos: acesso; protocolar; tramitar; consultar histórico; arquivar; tentativa bloqueada (tramitar arquivado). Ao final, link e credenciais do avaliador.
- Campo do vídeo narrado: "Demonstração apresentada no item X deste documento". Campo do vídeo da solução atualizada: "Correções evidenciadas no Laudo de Qualidade, item Y". Nunca em branco.
- Capturas com Playwright, dados de demonstração, resolução legível, em `docs/capturas/` com nome de fluxo e passo.

## Testes e laudo

- 5 a 10 testes pytest, foco nas regras de negócio; guardar a saída como evidência.
- Kit do testador em `docs/testadores/`: texto de contexto (até uma página), perguntas do formulário (nome; data do teste; o que testou e funcionou; o que testou e não funcionou e o que deve ser corrigido; funcionalidade não testada), convite curto.
- Nota: curso a distância sem turma fixa, testes feitos por usuários externos ao curso.
- Laudo: número; descrição; origem (testador ou "teste interno"); gravidade (alta, média, baixa); correção; evidência (antes e depois lado a lado); situação. Toda falha de testador aparece, corrigida ou justificada.

## Documentação

Escopo da versão (dentro e fora); requisitos funcionais e não funcionais; regras de negócio; casos de uso; diagrama de classes; manual de uso. Com PIT-I: abrir com tabela de revisão e lições aprendidas. Sem PIT-I: "consolidada nesta versão", sem afirmar revisão.

Diagramas por código, exportados como imagem, coerentes entre si e com `schema.sql`: classes (Mermaid), conceitual Peter Chen (Graphviz), lógico (Mermaid erDiagram).

## Fases

| Fase | Entregável |
|---|---|
| 0 | Perguntas iniciais, estrutura, DECISOES.md, .gitignore, Git local |
| 1 | Documentação (exceto manual) |
| 2 | Diagramas, schema.sql, dados de demonstração |
| 3 | Aplicação completa, commits por funcionalidade, instruções locais (aprovação após teste do usuário) |
| 4 | Testes próprios, correções, evidência |
| 5 | README, envio ao GitHub |
| 6 | Passo a passo PythonAnywhere |
| 7 | Kit do testador com link e credenciais reais |
| 8 | Capturas e seção de demonstração |
| 9 | Transcrição, correções, nova publicação, laudo |
| 10 | Template preenchido em `entrega/` |
| 11 | Revisão de estilo e coerência; lista de conferência de links |

## Alertas a fazer no momento certo

- Validade da aplicação no plano gratuito do PythonAnywhere e como renovar (fase 6).
- Conferir se a instituição exige declaração de uso de IA (fase 10).
- Reservar tempo para o aluno entender código e regras de negócio (fase 3 em diante).
