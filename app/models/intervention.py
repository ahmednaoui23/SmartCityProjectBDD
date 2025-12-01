import enum
from sqlalchemy import Column, BigInteger, TIMESTAMP, Integer, Numeric, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class InterventionNatureEnum(str, enum.Enum):
    predictive = "predictive"
    corrective = "corrective"
    curative = "curative"

class Intervention(Base):
    __tablename__ = "intervention"
    id_intervention = Column(BigInteger, primary_key=True, index=True)
    date_heure = Column(TIMESTAMP(timezone=True), nullable=False)
    nature = Column(Enum(InterventionNatureEnum))
    duree_minutes = Column(Integer)
    cout = Column(Numeric(12,2))
    impact_co2 = Column(Numeric(12,4))
    ia_valide = Column(Boolean, default=False)
    uuid_capteur = Column(ForeignKey("capteur.uuid_capteur"), nullable=True)

    capteur = relationship("Capteur", back_populates="interventions")
    realisers = relationship("Realiser", back_populates="intervention", cascade="all, delete-orphan")