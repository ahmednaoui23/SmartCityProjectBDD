from sqlite3 import IntegrityError

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, desc, case
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta

from app import models
from app.schemas import (
    proprietaire as sch_prop, capteur as sch_cap, mesure as sch_mes,
    technicien as sch_tech, intervention as sch_inter, realiser as sch_real,
    citoyen as sch_citoy, consultation as sch_cons, participer_a as sch_part,
    vehicule as sch_veh, trajet as sch_traj
)

# ---------------- Proprietaire ----------------

def create_proprietaire(db: Session, payload):
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

# ---------------- Analytics (ORM implementations) ----------------
def pollution_24h(db: Session, pollutant: str = "PM2.5", top_n: int = 10, order_by: str = "measure"):
    """
    ORM implementation (stable, self-contained) that returns the top arrondissements
    by pollution over the last 24 hours.

    Behavior:
    - Uses only capteurs considered 'active'. Resolved status = last capteur_status_history.status
      when present, otherwise capteur.statut.
    - Two metrics returned per arrondissement:
        * avg_by_measure : average of all mesures (weighted by number of mesures), rounded to 2 decimals
        * avg_by_sensor  : average of per-capteur averages (each capteur has equal weight), rounded to 2 decimals
    - Also returns nb_mesures, nb_capteurs and rank (1 = most polluted by chosen order).
    - Parameters:
        db        : SQLAlchemy Session
        pollutant : pollutant name (default 'PM2.5')
        top_n     : number of arrondissements to return
        order_by  : 'measure' (default) or 'sensor' to choose sorting key
    - Deterministic ordering: primary = chosen metric desc, secondary = nb_mesures desc, tertiary = id_arrondissement asc
    """
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import func, desc, asc, case

    if order_by not in ("measure", "sensor"):
        raise ValueError("order_by must be 'measure' or 'sensor'")

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    # Subquery: latest status timestamp per capteur
    last_ts_subq = (
        db.query(
            models.CapteurStatusHistory.uuid_capteur.label("uuid"),
            func.max(models.CapteurStatusHistory.ts).label("max_ts"),
        )
        .group_by(models.CapteurStatusHistory.uuid_capteur)
        .subquery()
    )

    # Subquery: last status row per capteur (uuid_capteur, status)
    last_status_subq = (
        db.query(
            models.CapteurStatusHistory.uuid_capteur.label("uuid_capteur"),
            models.CapteurStatusHistory.status.label("status"),
        )
        .join(
            last_ts_subq,
            (models.CapteurStatusHistory.uuid_capteur == last_ts_subq.c.uuid)
            & (models.CapteurStatusHistory.ts == last_ts_subq.c.max_ts),
        )
        .subquery()
    )

    # Active capteurs: those whose resolved status = 'active'
    active_caps_subq = (
        db.query(models.Capteur.uuid_capteur.label("uuid_capteur"))
        .outerjoin(last_status_subq, models.Capteur.uuid_capteur == last_status_subq.c.uuid_capteur)
        .filter(func.coalesce(last_status_subq.c.status, models.Capteur.statut) == "active")
        .subquery()
    )

    # Aggregate by measure (weighted by number of mesures)
    agg_by_measure_q = (
        db.query(
            models.Capteur.id_arrondissement.label("id_arrondissement"),
            models.Arrondissement.nom.label("nom"),
            func.round(func.avg(models.Mesure.valeur), 2).label("avg_by_measure"),
            func.count(models.Mesure.id).label("nb_mesures"),
            func.count(func.distinct(models.Mesure.uuid_capteur)).label("nb_capteurs"),
        )
        .join(models.Capteur, models.Mesure.uuid_capteur == models.Capteur.uuid_capteur)
        .join(models.Arrondissement, models.Capteur.id_arrondissement == models.Arrondissement.id_arrondissement)
        .join(active_caps_subq, models.Capteur.uuid_capteur == active_caps_subq.c.uuid_capteur)
        .filter(
            models.Mesure.pollutant == pollutant,
            models.Mesure.ts >= cutoff,
        )
        .group_by(models.Capteur.id_arrondissement, models.Arrondissement.nom)
    ).subquery()

    # Per-sensor average over the window
    per_sensor_q = (
        db.query(
            models.Mesure.uuid_capteur.label("uuid_capteur"),
            models.Capteur.id_arrondissement.label("id_arrondissement"),
            models.Arrondissement.nom.label("nom"),
            func.avg(models.Mesure.valeur).label("avg_val"),
        )
        .join(models.Capteur, models.Mesure.uuid_capteur == models.Capteur.uuid_capteur)
        .join(models.Arrondissement, models.Capteur.id_arrondissement == models.Arrondissement.id_arrondissement)
        .join(active_caps_subq, models.Capteur.uuid_capteur == active_caps_subq.c.uuid_capteur)
        .filter(
            models.Mesure.pollutant == pollutant,
            models.Mesure.ts >= cutoff,
        )
        .group_by(models.Mesure.uuid_capteur, models.Capteur.id_arrondissement, models.Arrondissement.nom)
    ).subquery()

    # Aggregate by sensor averages (each sensor contributes equally)
    agg_by_sensor_q = (
        db.query(
            per_sensor_q.c.id_arrondissement.label("id_arrondissement"),
            per_sensor_q.c.nom.label("nom"),
            func.round(func.avg(per_sensor_q.c.avg_val), 2).label("avg_by_sensor"),
        )
        .group_by(per_sensor_q.c.id_arrondissement, per_sensor_q.c.nom)
    ).subquery()

    # Final join: combine both metrics
    final_q = (
        db.query(
            agg_by_measure_q.c.id_arrondissement,
            agg_by_measure_q.c.nom,
            agg_by_measure_q.c.avg_by_measure,
            agg_by_sensor_q.c.avg_by_sensor,
            agg_by_measure_q.c.nb_mesures,
            agg_by_measure_q.c.nb_capteurs,
        )
        .outerjoin(
            agg_by_sensor_q,
            (agg_by_measure_q.c.id_arrondissement == agg_by_sensor_q.c.id_arrondissement)
            & (agg_by_measure_q.c.nom == agg_by_sensor_q.c.nom),
        )
    )

    # Determine ordering
    if order_by == "sensor":
        # order by sensor metric first (nulls last), then nb_mesures, then id
        final_q = final_q.order_by(
            desc(agg_by_sensor_q.c.avg_by_sensor.nullslast()),
            desc(agg_by_measure_q.c.nb_mesures),
            asc(agg_by_measure_q.c.id_arrondissement),
        )
    else:
        final_q = final_q.order_by(
            desc(agg_by_measure_q.c.avg_by_measure.nullslast()),
            desc(agg_by_measure_q.c.nb_mesures),
            asc(agg_by_measure_q.c.id_arrondissement),
        )

    final_q = final_q.limit(top_n)
    results = final_q.all()

    # Normalize and add rank
    out = []
    for idx, row in enumerate(results, start=1):
        mapping = getattr(row, "_mapping", None)
        if mapping is not None:
            m = mapping
            out.append({
                "rank": idx,

                "nom": m["nom"],
                "avg_by_measure": float(m["avg_by_measure"]) if m["avg_by_measure"] is not None else None,
                "avg_by_sensor": float(m["avg_by_sensor"]) if m["avg_by_sensor"] is not None else None,
                "nb_mesures": int(m["nb_mesures"]) if m["nb_mesures"] is not None else 0,
                "nb_capteurs": int(m["nb_capteurs"]) if m["nb_capteurs"] is not None else 0,
            })
        else:
            out.append({
                "rank": idx,

                "nom": row[1],
                "avg_by_measure": float(row[2]) if row[2] is not None else None,
                "avg_by_sensor": float(row[3]) if row[3] is not None else None,
                "nb_mesures": int(row[4]) if row[4] is not None else 0,
                "nb_capteurs": int(row[5]) if row[5] is not None else 0,
            })

    return out

def availability_by_arrondissement(db: Session):
    """
    ORM implementation:
    - For each arrondissement compute percent of capteurs whose resolved status = 'active'
      where resolved status = last capteur_status_history.status if exists, else capteur.statut.
    - Returns list of dicts {id_arrondissement, nom, pct_active}.
    """
    # last status timestamp per capteur
    last_ts_subq = (
        db.query(
            models.CapteurStatusHistory.uuid_capteur.label("uuid"),
            func.max(models.CapteurStatusHistory.ts).label("max_ts"),
        )
        .group_by(models.CapteurStatusHistory.uuid_capteur)
        .subquery()
    )

    last_status_subq = (
        db.query(
            models.CapteurStatusHistory.uuid_capteur.label("uuid_capteur"),
            models.CapteurStatusHistory.status.label("status"),
        )
        .join(
            last_ts_subq,
            (models.CapteurStatusHistory.uuid_capteur == last_ts_subq.c.uuid)
            & (models.CapteurStatusHistory.ts == last_ts_subq.c.max_ts),
        )
        .subquery()
    )

    # Build expression counting active capteurs
    active_expr = func.sum(
        case(
            [(func.coalesce(last_status_subq.c.status, models.Capteur.statut) == "active", 1)],
            else_=0,
        )
    ).label("active_count")

    total_expr = func.count(models.Capteur.uuid_capteur).label("total_count")

    q = (
        db.query(
            models.Arrondissement.id_arrondissement,
            models.Arrondissement.nom,
            (100.0 * active_expr / func.nullif(total_expr, 0)).label("pct_active"),
        )
        .join(models.Capteur, models.Arrondissement.id_arrondissement == models.Capteur.id_arrondissement, isouter=False)
        .outerjoin(last_status_subq, models.Capteur.uuid_capteur == last_status_subq.c.uuid_capteur)
        .group_by(models.Arrondissement.id_arrondissement, models.Arrondissement.nom)
        .order_by(desc("pct_active"))
    )

    results = q.all()
    out = []
    for row in results:
        mapping = getattr(row, "_mapping", None)
        if mapping is not None:
            m = mapping
            pct = float(m["pct_active"]) if m["pct_active"] is not None else 0.0
            out.append({
                "id_arrondissement": m["id_arrondissement"],
                "nom": m["nom"],
                "pct_active": round(pct, 2),
            })
        else:
            pct = float(row[2]) if row[2] is not None else 0.0
            out.append({
                "id_arrondissement": row[0],
                "nom": row[1],
                "pct_active": round(pct, 2),
            })
    return out

def citizens_most_engaged(db: Session, limit=20):
    return db.query(models.Citoyen).order_by(models.Citoyen.score_engagement.desc()).limit(limit).all()

def predictive_this_month(db: Session):
    """
    ORM implementation: count predictive interventions this month and sum impact_co2
    """
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # compute first day of next month
    if start.month == 12:
        next_month = start.replace(year=start.year + 1, month=1)
    else:
        next_month = start.replace(month=start.month + 1)
    q = db.query(
        func.count(models.Intervention.id_intervention).label("nb_predictives"),
        func.coalesce(func.sum(models.Intervention.impact_co2), 0).label("total_co2_saved"),
    ).filter(
        models.Intervention.nature == "predictive",
        models.Intervention.date_heure >= start,
        models.Intervention.date_heure < next_month,
    )
    row = q.first()
    return {
        "nb_predictives": int(row.nb_predictives) if row and row.nb_predictives is not None else 0,
        "total_co2_saved": float(row.total_co2_saved) if row and row.total_co2_saved is not None else 0.0,
    }

def top_trajets(db: Session, limit=20):
    q = (
        db.query(
            models.Trajet.id_trajet,
            models.Trajet.origine,
            models.Trajet.destination,
            models.Trajet.co2_economie,
        )
        .filter(models.Trajet.co2_economie.isnot(None))
        .order_by(models.Trajet.co2_economie.desc())
        .limit(limit)
    )
    results = q.all()
    out = []
    for row in results:
        mapping = getattr(row, "_mapping", None)
        if mapping is not None:
            m = mapping
            out.append({
                "id_trajet": m["id_trajet"],
                "origine": m["origine"],
                "destination": m["destination"],
                "co2_economie": float(m["co2_economie"]) if m["co2_economie"] is not None else None,
            })
        else:
            out.append({
                "id_trajet": row[0],
                "origine": row[1],
                "destination": row[2],
                "co2_economie": float(row[3]) if row[3] is not None else None,
            })
    return out