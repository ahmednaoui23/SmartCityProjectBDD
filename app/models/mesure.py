from sqlalchemy import Column, BigInteger, TIMESTAMP, String, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class Mesure(Base):
    __tablename__ = "mesure"
    id = Column(BigInteger, primary_key=True, index=True)
    uuid_capteur = Column(UUID(as_uuid=True), ForeignKey("capteur.uuid_capteur", ondelete="CASCADE"), nullable=False)
    ts = Column(TIMESTAMP(timezone=True), nullable=False)
    pollutant = Column(String(100), nullable=False)
    valeur = Column(Numeric(14,6), nullable=False)
    unite = Column(String(30))

    capteur = relationship("Capteur", back_populates="mesures")