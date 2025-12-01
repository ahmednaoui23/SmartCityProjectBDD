import enum, uuid
from sqlalchemy import Column, String, Numeric, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class CapteurStatusEnum(str, enum.Enum):
    active = "active"
    maintenance = "maintenance"
    out_of_service = "out_of_service"
    failed = "failed"

class Capteur(Base):
    __tablename__ = "capteur"
    uuid_capteur = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_capteur = Column(String(100), nullable=False)
    latitude = Column(Numeric(9,6))
    longitude = Column(Numeric(9,6))
    statut = Column(Enum(CapteurStatusEnum), default=CapteurStatusEnum.active)
    date_installation = Column(TIMESTAMP(timezone=True))
    id_proprietaire = Column(ForeignKey("proprietaire.id_proprietaire"), nullable=True)
    id_arrondissement = Column(ForeignKey("arrondissement.id_arrondissement"), nullable=True)

    proprietaire = relationship("Proprietaire", back_populates="capteurs")
    arrondissement = relationship("Arrondissement", back_populates="capteurs")
    mesures = relationship("Mesure", back_populates="capteur", cascade="all, delete-orphan")
    status_history = relationship("CapteurStatusHistory", back_populates="capteur", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="capteur")