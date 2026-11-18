-- Projeto físico do Sistema de Protocolo e Tramitação
-- Prefeitura Municipal de Vila Serena (órgão fictício)
-- Compatível com MySQL 8.0.16 ou superior (CHECK constraints ativas).

SET NAMES utf8mb4;

DROP TABLE IF EXISTS tramitacao;
DROP TABLE IF EXISTS documento;
DROP TABLE IF EXISTS interessado;
DROP TABLE IF EXISTS usuario;
DROP TABLE IF EXISTS setor;

CREATE TABLE setor (
    id_setor     INT          NOT NULL AUTO_INCREMENT,
    nome         VARCHAR(80)  NOT NULL,
    sigla        VARCHAR(10)  NOT NULL,
    -- Indica o setor que recebe os documentos protocolados (regra 2).
    eh_protocolo TINYINT(1)   NOT NULL DEFAULT 0,
    CONSTRAINT pk_setor PRIMARY KEY (id_setor),
    CONSTRAINT uq_setor_nome UNIQUE (nome),
    CONSTRAINT uq_setor_sigla UNIQUE (sigla),
    CONSTRAINT ck_setor_eh_protocolo CHECK (eh_protocolo IN (0, 1))
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE usuario (
    id_usuario  INT          NOT NULL AUTO_INCREMENT,
    nome        VARCHAR(100) NOT NULL,
    login       VARCHAR(30)  NOT NULL,
    senha_hash  VARCHAR(255) NOT NULL,
    perfil      VARCHAR(15)  NOT NULL DEFAULT 'servidor',
    id_setor    INT          NOT NULL,
    CONSTRAINT pk_usuario PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuario_login UNIQUE (login),
    CONSTRAINT ck_usuario_perfil CHECK (perfil IN ('administrador', 'servidor')),
    CONSTRAINT fk_usuario_setor FOREIGN KEY (id_setor) REFERENCES setor (id_setor)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE interessado (
    id_interessado INT          NOT NULL AUTO_INCREMENT,
    nome           VARCHAR(120) NOT NULL,
    -- Somente dígitos: 11 para CPF, 14 para CNPJ (regra 7).
    cpf_cnpj       VARCHAR(14)  NOT NULL,
    telefone       VARCHAR(20)  NULL,
    email          VARCHAR(120) NULL,
    CONSTRAINT pk_interessado PRIMARY KEY (id_interessado),
    CONSTRAINT uq_interessado_cpf_cnpj UNIQUE (cpf_cnpj),
    CONSTRAINT ck_interessado_cpf_cnpj CHECK (CHAR_LENGTH(cpf_cnpj) IN (11, 14))
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE documento (
    id_documento      INT          NOT NULL AUTO_INCREMENT,
    -- Formato AAAA/NNNNN (regra 1). Ano e sequencial ficam separados para
    -- garantir a unicidade por ano e facilitar o cálculo do próximo número.
    numero_protocolo  CHAR(10)     NOT NULL,
    ano               SMALLINT     NOT NULL,
    sequencial        INT          NOT NULL,
    tipo              VARCHAR(20)  NOT NULL,
    assunto           VARCHAR(200) NOT NULL,
    data_protocolo    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    situacao          VARCHAR(15)  NOT NULL DEFAULT 'Em tramitação',
    data_arquivamento DATETIME     NULL,
    id_interessado    INT          NOT NULL,
    id_setor_atual    INT          NOT NULL,
    CONSTRAINT pk_documento PRIMARY KEY (id_documento),
    CONSTRAINT uq_documento_numero UNIQUE (numero_protocolo),
    CONSTRAINT uq_documento_ano_seq UNIQUE (ano, sequencial),
    CONSTRAINT ck_documento_sequencial CHECK (sequencial BETWEEN 1 AND 99999),
    CONSTRAINT ck_documento_tipo CHECK (tipo IN ('Requerimento', 'Ofício', 'Memorando', 'Denúncia', 'Outro')),
    CONSTRAINT ck_documento_situacao CHECK (situacao IN ('Em tramitação', 'Arquivado')),
    CONSTRAINT ck_documento_arquivamento CHECK (
        (situacao = 'Arquivado' AND data_arquivamento IS NOT NULL)
        OR (situacao = 'Em tramitação' AND data_arquivamento IS NULL)
    ),
    CONSTRAINT fk_documento_interessado FOREIGN KEY (id_interessado) REFERENCES interessado (id_interessado),
    CONSTRAINT fk_documento_setor FOREIGN KEY (id_setor_atual) REFERENCES setor (id_setor)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE tramitacao (
    id_tramitacao   INT          NOT NULL AUTO_INCREMENT,
    id_documento    INT          NOT NULL,
    -- Nulo apenas no registro de entrada criado pelo protocolo (regra 2).
    id_setor_origem INT          NULL,
    id_setor_destino INT         NOT NULL,
    data_hora       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    despacho        VARCHAR(500) NOT NULL,
    id_usuario      INT          NOT NULL,
    CONSTRAINT pk_tramitacao PRIMARY KEY (id_tramitacao),
    CONSTRAINT ck_tramitacao_destino CHECK (id_setor_origem IS NULL OR id_setor_origem <> id_setor_destino),
    CONSTRAINT fk_tramitacao_documento FOREIGN KEY (id_documento) REFERENCES documento (id_documento),
    CONSTRAINT fk_tramitacao_origem FOREIGN KEY (id_setor_origem) REFERENCES setor (id_setor),
    CONSTRAINT fk_tramitacao_destino FOREIGN KEY (id_setor_destino) REFERENCES setor (id_setor),
    CONSTRAINT fk_tramitacao_usuario FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE INDEX ix_documento_setor ON documento (id_setor_atual, situacao);
CREATE INDEX ix_tramitacao_documento ON tramitacao (id_documento, data_hora);
