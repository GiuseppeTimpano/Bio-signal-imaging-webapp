from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Bioimage(Base):

    __tablename__ = 'bioimage'

    id: Mapped[int] = mapped_column(primary_key=True)
    patient: Mapped[str] = mapped_column()

    def _repr_(self):
        return f"Bioimage('{ self.id}', '{ self.patient}')"

from sqlalchemy import create_engine
engine = create_engine("sqlite://", echo=True)

Base.metadata.create_all(engine)