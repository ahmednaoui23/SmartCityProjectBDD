from sqlalchemy import Column, BigInteger, ForeignKey, Text, SmallInteger, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base

class ParticiperA(Base):
    __tablename__ = "participer_a"
    id_citoyen = Column(BigInteger, ForeignKey("citoyen.id_citoyen", ondelete="CASCADE"), primary_key=True)
    id_consultation = Column(BigInteger, ForeignKey("consultation.id_consultation", ondelete="CASCADE"), primary_key=True)
    avis = Column(Text)
    vote = Column(SmallInteger)
    date_participation = Column(TIMESTAMP(timezone=True))

    citoyen = relationship("Citoyen", back_populates="participations")
    consultation = relationship("Consultation", back_populates="participants")