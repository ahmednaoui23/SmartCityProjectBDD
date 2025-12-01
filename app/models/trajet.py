from sqlalchemy import Column, BigInteger, Text, Numeric, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Trajet(Base):
    __tablename__ = "trajet"
    id_trajet = Column(BigInteger, primary_key=True, index=True)
    origine = Column(Text)
    destination = Column(Text)
    distance_km = Column(Numeric(9,3))
    duree_minutes = Column(Integer)
    co2_economie = Column(Numeric(12,4))
    date_heure = Column(TIMESTAMP(timezone=True))
    plaque = Column(ForeignKey("vehicule.plaque"))

    vehicule = relationship("Vehicule", back_populates="trajets")