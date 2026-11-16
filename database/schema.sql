-- BarberAgenda - modelo físico (MySQL 8)

CREATE TABLE usuario (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    email       VARCHAR(120) NOT NULL,
    senha_hash  VARCHAR(255) NOT NULL,
    perfil      ENUM('administrador', 'recepcionista') NOT NULL DEFAULT 'recepcionista',
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_usuario_email UNIQUE (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE cliente (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    nome      VARCHAR(100) NOT NULL,
    telefone  VARCHAR(20)  NOT NULL,
    email     VARCHAR(120) NULL,
    ativo     BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE profissional (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    telefone     VARCHAR(20) NULL,
    hora_inicio  TIME NOT NULL,
    hora_fim     TIME NOT NULL,
    ativo        BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_profissional_horario CHECK (hora_fim > hora_inicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE servico (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    preco        DECIMAL(8,2) NOT NULL,
    duracao_min  INT NOT NULL,
    ativo        BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_servico_preco CHECK (preco >= 0),
    CONSTRAINT ck_servico_duracao CHECK (duracao_min BETWEEN 5 AND 480)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE agendamento (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id           INT NOT NULL,
    profissional_id      INT NOT NULL,
    servico_id           INT NOT NULL,
    usuario_id           INT NOT NULL,
    inicio               DATETIME NOT NULL,
    fim                  DATETIME NOT NULL,
    preco_cobrado        DECIMAL(8,2) NOT NULL,
    status               ENUM('agendado', 'concluido', 'cancelado') NOT NULL DEFAULT 'agendado',
    motivo_cancelamento  VARCHAR(255) NULL,
    criado_em            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_agendamento_cliente      FOREIGN KEY (cliente_id)      REFERENCES cliente(id),
    CONSTRAINT fk_agendamento_profissional FOREIGN KEY (profissional_id) REFERENCES profissional(id),
    CONSTRAINT fk_agendamento_servico      FOREIGN KEY (servico_id)      REFERENCES servico(id),
    CONSTRAINT fk_agendamento_usuario      FOREIGN KEY (usuario_id)      REFERENCES usuario(id),
    CONSTRAINT ck_agendamento_periodo      CHECK (fim > inicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Índices
CREATE INDEX ix_agendamento_profissional_inicio ON agendamento (profissional_id, inicio);
CREATE INDEX ix_agendamento_status_inicio ON agendamento (status, inicio);
