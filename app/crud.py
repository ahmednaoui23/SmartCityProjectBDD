from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from uuid import UUID

from app import models
from app.schemas import (
    proprietaire as sch_prop, capteur as sch_cap, mesure as sch_mes,
    technicien as sch_tech, intervention as sch_inter, realiser as sch_real,
    citoyen as sch_citoy, consultation as sch_cons, participer_a as sch_part,
    vehicule as sch_veh, trajet as sch_traj
)

# ---------------- Proprietaire ----------------
def create_proprietaire(db: Session, payload: sch_prop.ProprietaireCreate):
    obj = models.Proprietaire(**payload.dict())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def get_proprietaire(db: Session, id_: int):
    return db.query(models.Proprietaire).filter(models.Proprietaire.id_proprietaire==id_).first()

def list_proprietaires(db: Session, skip=0, limit=100):
    return db.query(models.Proprietaire).offset(skip).limit(limit).all()

# ---------------- Capteur ----------------
def create_capteur(db: Session, payload: sch_cap.CapteurCreate):
    obj = models.Capteur(**payload.dict())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj

def get_capteur(db: Session, uuid: UUID):
    return db.query(models.Capteur).filter(models.Capteur.uuid_capteur==uuid).first()

def list_capteurs(db: Session, skip=0, limit=100):
    return db.query(models.Capteur).offset(skip).limit(limit).all()

def update_capteur(db: Session, uuid: UUID, payload: sch_cap.CapteurCreate):
    obj = get_capteur(db, uuid)
    if not obj:
        return None
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj); db.commit(); db.refresh(obj); return obj

def delete_capteur(db: Session, uuid: UUID):
    obj = get_capteur(db, uuid)
    if not obj: return False
    db.delete(obj); db.commit(); return True

# ---------------- Mesure ----------------
def create_mesure(db: Session, payload: sch_mes.MesureCreate):
    # validate capteur exist
    cap = get_capteur(db, payload.uuid_capteur)
    if not cap:
        raise ValueError("Capteur not found")
    obj = models.Mesure(**payload.dict())
    db.add(obj); db.commit(); db.refresh(obj); return obj

def list_mesures(db: Session, limit=100):
    return db.query(models.Mesure).order_by(models.Mesure.ts.desc()).limit(limit).all()

# ---------------- Capteur status history ----------------
def create_status(db: Session, uuid: UUID, status: str, ts=None):
    cap = get_capteur(db, uuid)
    if not cap:
        raise ValueError("Capteur not found")
    obj = models.CapteurStatusHistory(uuid_capteur=uuid, status=status, ts=ts)
    db.add(obj); db.commit(); db.refresh(obj); return obj

# ---------------- Technicien ----------------
def create_technicien(db: Session, payload: sch_tech.TechnicienCreate):
    obj = models.Technicien(**payload.dict())
    db.add(obj); db.commit(); db.refresh(obj); return obj

def list_techniciens(db: Session, skip=0, limit=100):
    return db.query(models.Technicien).offset(skip).limit(limit).all()

def get_technicien(db: Session, id_: int):
    return db.query(models.Technicien).filter(models.Technicien.id_technicien==id_).first()

# ---------------- Intervention ----------------
def create_intervention(db: Session, payload: sch_inter.InterventionCreate):
    obj = models.Intervention(**payload.dict())
    db.add(obj); db.commit(); db.refresh(obj); return obj

def get_intervention(db: Session, id_: int):
    return db.query(models.Intervention).filter(models.Intervention.id_intervention==id_).first()

def list_interventions(db: Session, skip=0, limit=100):
    return db.query(models.Intervention).order_by(models.Intervention.date_heure.desc()).offset(skip).limit(limit).all()

# ---------------- Realiser (association) ----------------
def add_realiser(db: Session, payload: sch_real.RealiserCreate):
    # validate existence
    inter = get_intervention(db, payload.id_intervention)
    tech = get_technicien(db, payload.id_technicien)
    if not inter or not tech:
        raise ValueError("Intervention or Technicien not found")
    existing = db.query(models.Realiser).filter(
        models.Realiser.id_intervention==payload.id_intervention,
        models.Realiser.id_technicien==payload.id_technicien
    ).first()
    if existing:
        return existing
    obj = models.Realiser(id_intervention=payload.id_intervention, id_technicien=payload.id_technicien, role=payload.role)
    db.add(obj); db.commit(); db.refresh(obj); return obj

def remove_realiser(db: Session, id_intervention: int, id_technicien: int):
    obj = db.query(models.Realiser).filter(
        models.Realiser.id_intervention==id_intervention,
        models.Realiser.id_technicien==id_technicien
    ).first()
    if not obj:
        return False
    db.delete(obj); db.commit(); return True

def count_realisers(db: Session, id_intervention: int):
    return db.query(models.Realiser).filter(models.Realiser.id_intervention==id_intervention).count()

def close_intervention(db: Session, id_intervention: int):
    inter = get_intervention(db, id_intervention)
    if not inter:
        raise ValueError("Intervention not found")
    n = count_realisers(db, id_intervention)
    if n < 2:
        raise ValueError("Intervention must have at least 2 technicians before closing")
    inter.ia_valide = True
    db.add(inter); db.commit(); db.refresh(inter); return inter

# ---------------- Citoyen / Consultation / Participations ----------------
def create_citoyen(db: Session, payload: sch_citoy.CitoyenCreate):
    obj = models.Citoyen(**payload.dict())
    db.add(obj); db.commit(); db.refresh(obj); return obj

def list_citoyens(db: Session, skip=0, limit=100):
    return db.query(models.Citoyen).offset(skip).limit(limit).all()

def create_consultation(db: Session, payload: sch_cons.ConsultationCreate):
    obj = models.Consultation(**payload.dict())
    db.add(obj); db.commit(); db.refresh(obj); return obj

def create_participation(db: Session, payload: sch_part.ParticiperACreate):
    c = db.query(models.Citoyen).get(payload.id_citoyen)
    con = db.query(models.Consultation).get(payload.id_consultation)
    if not c or not con:
        raise ValueError("Citoyen or Consultation not found")
    obj = models.ParticiperA(**payload.dict())
    db.add(obj); db.commit(); db.refresh(obj); return obj

# ---------------- Vehicule / Trajet ----------------
def create_vehicule(db: Session, payload: sch_veh.VehiculeCreate):
    obj = models.Vehicule(**payload.dict())
    db.add(obj); db.commit(); db.refresh(obj); return obj

def create_trajet(db: Session, payload: sch_veh.TrajetCreate):
    if payload.plaque:
        v = db.query(models.Vehicule).filter(models.Vehicule.plaque==payload.plaque).first()
        if not v:
            raise ValueError("Vehicule not found")
    obj = models.Trajet(**payload.dict())
    db.add(obj); db.commit(); db.refresh(obj); return obj

# ---------------- Analytics (raw SQL) ----------------
def pollution_24h(db: Session):
    sql = """
    SELECT a.id_arrondissement, a.nom, AVG(m.valeur)::float AS avg_pm25
    FROM mesure m
    JOIN capteur c ON m.uuid_capteur = c.uuid_capteur
    JOIN arrondissement a ON c.id_arrondissement = a.id_arrondissement
    WHERE m.pollutant = 'PM2.5' AND m.ts >= now() - interval '24 hours'
    GROUP BY a.id_arrondissement, a.nom
    ORDER BY avg_pm25 DESC;
    """
    return db.execute(text(sql)).fetchall()

def availability_by_arrondissement(db: Session):
    sql = """
    WITH last_status AS (
      SELECT DISTINCT ON (uuid_capteur) uuid_capteur, status
      FROM capteur_status_history
      ORDER BY uuid_capteur, ts DESC
    )
    SELECT a.id_arrondissement, a.nom,
           100.0 * SUM(CASE WHEN ls.status = 'active' THEN 1 ELSE 0 END) / NULLIF(COUNT(c.uuid_capteur),0) AS pct_active
    FROM capteur c
    LEFT JOIN last_status ls ON c.uuid_capteur = ls.uuid_capteur
    LEFT JOIN arrondissement a ON c.id_arrondissement = a.id_arrondissement
    GROUP BY a.id_arrondissement, a.nom
    ORDER BY pct_active DESC;
    """
    return db.execute(text(sql)).fetchall()

def citizens_most_engaged(db: Session, limit=20):
    return db.query(models.Citoyen).order_by(models.Citoyen.score_engagement.desc()).limit(limit).all()

def predictive_this_month(db: Session):
    sql = """
    SELECT COUNT(*) AS nb_predictives, COALESCE(SUM(impact_co2),0)::float AS total_co2_saved
    FROM intervention
    WHERE nature = 'predictive' AND date_heure >= date_trunc('month', now()) AND date_heure < (date_trunc('month', now()) + interval '1 month');
    """
    return db.execute(text(sql)).first()

def top_trajets(db: Session, limit=20):
    sql = """
    SELECT id_trajet, origine, destination, co2_economie
    FROM trajet
    WHERE co2_economie IS NOT NULL
    ORDER BY co2_economie DESC
    LIMIT :lim;
    """
    return db.execute(text(sql), {"lim": limit}).fetchall()