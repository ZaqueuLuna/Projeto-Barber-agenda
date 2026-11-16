from app import db


class Profissional(db.Model):
    __tablename__ = "profissional"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
