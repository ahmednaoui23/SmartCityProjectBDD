from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base

class Vehicule(Base):
    __tablename__ = "vehicule"
    plaque = Column(String(20), primary_key=True)
    type_vehicule = Column(String(100))
    energie = Column(String(50))

    trajets = relationship("Trajet", back_populates="vehicule")