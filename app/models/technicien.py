from sqlalchemy import Column, BigInteger, Text, String
from sqlalchemy.orm import relationship
from app.database import Base

class Technicien(Base):
    __tablename__ = "technicien"
    id_technicien = Column(BigInteger, primary_key=True, index=True)
    nom = Column(Text, nullable=False)
    telephone = Column(String(50))
    certification = Column(Text)

    realisations = relationship("Realiser", back_populates="technicien")