from sqlalchemy import Column, BigInteger, Text, String
from sqlalchemy.orm import relationship
from app.database import Base

class Proprietaire(Base):
    __tablename__ = "proprietaire"

    id_proprietaire = Column(BigInteger, primary_key=True, index=True)
    nom = Column(Text, nullable=False)
    adresse = Column(Text)
    telephone = Column(String(50))
    email = Column(String(255), unique=True)
    type_proprietaire = Column(String(100))

    capteurs = relationship("Capteur", back_populates="proprietaire")
