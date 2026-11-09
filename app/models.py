from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class Documento(Base):
    """Uma linha por registro do app (produto, cliente, venda ou movimentação).

    Usa JSONB no PostgreSQL (e JSON simples no SQLite, só para testes locais).
    O front trata cada coleção como uma lista de objetos com "id".
    """

    __tablename__ = "documentos"

    colecao: Mapped[str] = mapped_column(String(32), primary_key=True)
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dados: Mapped[dict] = mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)
