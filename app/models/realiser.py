from sqlalchemy import Column, BigInteger, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base

class Realiser(Base):
    __tablename__ = "realiser"
    id_intervention = Column(BigInteger, ForeignKey("intervention.id_intervention", ondelete="CASCADE"), primary_key=True)
    id_technicien = Column(BigInteger, ForeignKey("technicien.id_technicien", ondelete="RESTRICT"), primary_key=True)
    role = Column(String(100), nullable=False)

    intervention = relationship("Intervention", back_populates="realisers")
    technicien = relationship("Technicien", back_populates="realisations")