from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud

router = APIRouter()

@router.get("/pollution_24h")
def pollution_24h(db: Session = Depends(get_db)):
    rows = crud.pollution_24h(db)
    return [{"id_arrondissement": r[0], "nom": r[1], "avg_pm25": float(r[2]) if r[2] is not None else None} for r in rows]

@router.get("/availability_by_arrondissement")
def availability(db: Session = Depends(get_db)):
    rows = crud.availability_by_arrondissement(db)
    return [{"id_arrondissement": r[0], "nom": r[1], "pct_active": float(r[2]) if r[2] is not None else None} for r in rows]

@router.get("/citizens_most_engaged")
def citizens_engaged(limit: int = 20, db: Session = Depends(get_db)):
    rows = crud.citizens_most_engaged(db, limit)
    return [{"id_citoyen": r.id_citoyen, "nom": r.nom, "score_engagement": float(r.score_engagement or 0)} for r in rows]

@router.get("/predictive_this_month")
def predictive_this_month(db: Session = Depends(get_db)):
    row = crud.predictive_this_month(db)
    return {"nb_predictives": int(row[0]), "total_co2_saved": float(row[1])}

@router.get("/top_trajets")
def top_trajets(limit: int = 20, db: Session = Depends(get_db)):
    rows = crud.top_trajets(db, limit)
    return [{"id_trajet": r[0], "origine": r[1], "destination": r[2], "co2_economie": float(r[3] or 0)} for r in rows]