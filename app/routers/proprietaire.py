
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.schemas import proprietaire as sch
from app import models

router = APIRouter()

@router.post("/", response_model=sch.ProprietaireOut, status_code=status.HTTP_201_CREATED)
def create_proprietaire(payload: sch.ProprietaireCreate, db: Session = Depends(get_db)):
    # Vérifier email existant
    existing = db.query(models.Proprietaire).filter(models.Proprietaire.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    obj = models.Proprietaire(**payload.dict())
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    db.refresh(obj)

    # Retour explicite en dict (évite tout souci de orm_mode)
    return {
        "nom": obj.nom,
        "adresse": obj.adresse,
        "telephone": obj.telephone,
        "email": obj.email,
        "type_proprietaire": obj.type_proprietaire,
    }

@router.get("/", response_model=list[sch.ProprietaireOut])
def list_proprietaires(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Proprietaire).offset(skip).limit(limit).all()

@router.get("/{id_}", response_model=sch.ProprietaireOut)
def get_one(id_: int, db: Session = Depends(get_db)):
    obj = db.query(models.Proprietaire).filter(models.Proprietaire.id_proprietaire == id_).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Proprietaire not found")
    return obj
