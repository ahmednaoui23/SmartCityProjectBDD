from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Arrondissement(Base):
    __tablename__ = "arrondissement"
    id_arrondissement = Column(Integer, primary_key=True)
    nom = Column(String(100), unique=True, nullable=False)

    capteurs = relationship("Capteur", back_populates="arrondissement")