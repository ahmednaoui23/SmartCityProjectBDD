from sqlalchemy import Column, BigInteger, Text, TIMESTAMP, String
from sqlalchemy.orm import relationship
from app.database import Base

class Consultation(Base):
    __tablename__ = "consultation"
    id_consultation = Column(BigInteger, primary_key=True, index=True)
    titre = Column(Text)
    date_consultation = Column(TIMESTAMP(timezone=True))
    theme = Column(String(200))

    participants = relationship("ParticiperA", back_populates="consultation", cascade="all, delete-orphan")