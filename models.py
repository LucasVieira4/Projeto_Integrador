from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    login = Column(String(50), unique=True, nullable=False)
    senha = Column(String(100), nullable=False)
    setor = Column(Enum('educacao', 'saude', 'tributario'), nullable=False)


class Senha(Base):
    __tablename__ = 'atendimentos'

    id = Column(Integer, primary_key=True)
    senha = Column(String(10), nullable=False)

    setor = Column(Enum('educacao', 'saude', 'tributario'), nullable=False)
    servico = Column(Enum(
        'clinico geral', 'pediatria', 'ortopedia', 'odontologia', 'vacinas',
        'iptu', 'iss', 'alvara', 'divida', 'certidoes', 'cadastro',
        'matriculas', 'documentos', 'transporte', 'creches', 'inclusao', 'geral'
    ), nullable=False)

    tipo = Column(String(50), nullable=False)
    prioridade = Column(Integer, default=1)

    status = Column(String(20), default='aguardando')

    origem = Column(String(20))
    horario_agendado = Column(DateTime)
    confirmado = Column(Boolean, default=False)

    data_emissao = Column(DateTime, server_default=func.now())
    data_inicio_atendimento = Column(DateTime)
    data_fim_atendimento = Column(DateTime)

    atendente_id = Column(Integer, ForeignKey('usuarios.id'))

    nome_paciente = Column(String(100))
    endereco = Column(String(200))
    data_nascimento = Column(String(20))
    filiacao = Column(String(200))