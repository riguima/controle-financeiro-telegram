from typing import List

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import ForeignKey

from controle_financeiro_telegram.database import db


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = 'clientes'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str]
    projetos: Mapped[List['Project']] = relationship(
        back_populates='cliente', cascade='all, delete-orphan'
    )


class Project(Base):
    __tablename__ = 'projetos'
    id: Mapped[int] = mapped_column(primary_key=True)
    cliente: Mapped['Client'] = relationship(back_populates='projetos')
    cliente_id: Mapped[int] = mapped_column(ForeignKey('clientes.id'))
    recebimentos: Mapped[List['Receipt']] = relationship(
        back_populates='projeto', cascade='all, delete-orphan'
    )
    valor_total: Mapped[float]
    entrada: Mapped[float]
    parcelas: Mapped[int]


class Receipt(Base):
    __tablename__ = 'recebimentos'
    id: Mapped[int] = mapped_column(primary_key=True)
    projeto: Mapped['Project'] = relationship(back_populates='recebimentos')
    projeto_id: Mapped[int] = mapped_column(ForeignKey('projetos.id'))
    valor: Mapped[float]


Base.metadata.create_all(db)
