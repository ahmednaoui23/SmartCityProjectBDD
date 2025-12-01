from sqlalchemy import Column, BigInteger, Text, String, Numeric, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Citoyen(Base):
    __tablename__ = "citoyen"
    id_citoyen = Column(BigInteger, primary_key=True, index=True)
    nom = Column(Text)
    adresse = Column(Text)
    email = Column(String(255), unique=True)
    score_engagement = Column(Numeric(8,2), default=0)
    preferences_mobilite = Column(JSON)

    participations = relationship("ParticiperA", back_populates="citoyen", cascade="all, delete-orphan")