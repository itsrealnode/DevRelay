from uuid import UUID, uuid4

from sqlalchemy import String, Text, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class ExampleBase(DeclarativeBase):
    pass


class ExampleModel(ExampleBase):
    __tablename__ = "examples"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
