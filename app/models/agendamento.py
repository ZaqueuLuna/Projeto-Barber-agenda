"""Agendamento e as regras de negócio RN01 a RN05."""
from datetime import datetime, timedelta

from app import db

STATUS_AGENDADO = "agendado"
STATUS_CONCLUIDO = "concluido"
STATUS_CANCELADO = "cancelado"


class ErroAgendamento(Exception):
    """Erro de regra de negócio."""


class Agendamento(db.Model):
    __tablename__ = "agendamento"
    __table_args__ = (db.Index("ix_agendamento_profissional_inicio", "profissional_id", "inicio"),)

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("cliente.id"), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissional.id"), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey("servico.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    inicio = db.Column(db.DateTime, nullable=False)
    fim = db.Column(db.DateTime, nullable=False)
    preco_cobrado = db.Column(db.Numeric(8, 2), nullable=False)
    status = db.Column(db.Enum(STATUS_AGENDADO, STATUS_CONCLUIDO, STATUS_CANCELADO,
                               name="status_agendamento"),
                       nullable=False, default=STATUS_AGENDADO)
    motivo_cancelamento = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, nullable=False, default=datetime.now)

    cliente = db.relationship("Cliente")
    profissional = db.relationship("Profissional")
    servico = db.relationship("Servico")
    usuario = db.relationship("Usuario")

    def conflita_com(self, outro):
        """RN01: verifica sobreposição de horário."""
        return self.inicio < outro.fim and self.fim > outro.inicio

    def concluir(self):
        if self.status != STATUS_AGENDADO:
            raise ErroAgendamento("Só é possível concluir um agendamento em aberto.")
        self.status = STATUS_CONCLUIDO

    def cancelar(self, motivo):
        if self.status != STATUS_AGENDADO:
            raise ErroAgendamento("Só é possível cancelar um agendamento em aberto.")
        if not motivo or not motivo.strip():
            raise ErroAgendamento("Informe o motivo do cancelamento.")
        self.status = STATUS_CANCELADO  # RN04: libera o horário
        self.motivo_cancelamento = motivo.strip()

    @property
    def status_texto(self):
        return {STATUS_AGENDADO: "Agendado", STATUS_CONCLUIDO: "Concluído",
                STATUS_CANCELADO: "Cancelado"}[self.status]


def salvar_agendamento(cliente, profissional, servico, inicio, usuario,
                       agendamento=None, agora=None):
    """Cria ou remarca um agendamento (RN01, RN02 e RN03)."""
    agora = agora or datetime.now()

    for item, nome in ((cliente, "cliente"), (profissional, "profissional"), (servico, "serviço")):
        if item is None or not item.ativo:
            raise ErroAgendamento(f"Escolha um {nome} ativo.")

    fim = inicio + timedelta(minutes=servico.duracao_min)

    # RN02
    if inicio < agora:
        raise ErroAgendamento("Esse horário já passou. Escolha uma data e hora futuras.")

    # RN03
    if (inicio.time() < profissional.hora_inicio or fim.time() > profissional.hora_fim
            or fim.date() != inicio.date()):
        raise ErroAgendamento(
            f"{profissional.nome} atende das {profissional.hora_inicio:%H:%M} "
            f"às {profissional.hora_fim:%H:%M}. Escolha um horário dentro desse período."
        )

    # RN01
    consulta = Agendamento.query.filter(
        Agendamento.profissional_id == profissional.id,
        Agendamento.status == STATUS_AGENDADO,
        Agendamento.inicio < fim,
        Agendamento.fim > inicio,
    )
    if agendamento is not None and agendamento.id is not None:
        consulta = consulta.filter(Agendamento.id != agendamento.id)
    conflito = consulta.first()
    if conflito:
        raise ErroAgendamento(
            f"Horário ocupado: {profissional.nome} atende {conflito.cliente.nome} "
            f"das {conflito.inicio:%H:%M} às {conflito.fim:%H:%M}."
        )

    if agendamento is None:
        agendamento = Agendamento(usuario_id=usuario.id, status=STATUS_AGENDADO)
        db.session.add(agendamento)
    elif agendamento.status != STATUS_AGENDADO:
        raise ErroAgendamento("Só é possível remarcar um agendamento em aberto.")

    if agendamento.servico_id != servico.id or agendamento.preco_cobrado is None:
        agendamento.preco_cobrado = servico.preco  # RN05

    agendamento.cliente_id = cliente.id
    agendamento.profissional_id = profissional.id
    agendamento.servico_id = servico.id
    agendamento.inicio = inicio
    agendamento.fim = fim
    return agendamento
