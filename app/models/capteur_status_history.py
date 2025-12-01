import enum
from sqlalchemy import Column, BigInteger, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from .capteur import CapteurStatusEnum

class CapteurStatusHistory(Base):
    __tablename__ = "capteur_status_history"
    id = Column(BigInteger, primary_key=True, index=True)
    uuid_capteur = Column(ForeignKey("capteur.uuid_capteur", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(CapteurStatusEnum), nullable=False)
    ts = Column(TIMESTAMP(timezone=True), nullable=False)

    capteur = relationship("Capteur", back_populates="status_history")