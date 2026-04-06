from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    login = Column(String(50), nullable=False, unique=True)
    senha = Column(String(100), nullable=False)
    setor = Column(Enum('educacao', 'saude', 'tributario'), nullable=False)


class Senha(Base):
    __tablename__ = 'atendimentos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    senha = Column(String(10), nullable=False)
    setor = Column(Enum('educacao', 'saude', 'tributario'), nullable=False)
    servico = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    prioridade = Column(String(20), default='normal')
    status = Column(String(20), default='aguardando')
    data_emissao = Column(DateTime, server_default=func.now())
    data_inicio_atendimento = Column(DateTime)
    data_fim_atendimento = Column(DateTime)
    atendente_id = Column(Integer, ForeignKey('usuarios.id'))
