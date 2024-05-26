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
    valor_total: Mapped[float]
    entrada: Mapped[float]
    parcelas: Mapped[int]


Base.metadata.create_all(db)
