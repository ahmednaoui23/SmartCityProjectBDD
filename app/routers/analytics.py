from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app import models

router = APIRouter()


def _pollution_24h(db: Session, pollutant: str = "PM2.5", top_n: int = 10, order_by: str = "measure"):
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

    # Determine ordering — use .desc().nullslast() on the column to produce "col DESC NULLS LAST"
    if order_by == "sensor":
        final_q = final_q.order_by(
            agg_by_sensor_q.c.avg_by_sensor.desc().nullslast(),
            agg_by_measure_q.c.nb_mesures.desc(),
            agg_by_measure_q.c.id_arrondissement.asc(),
        )
    else:
        final_q = final_q.order_by(
            agg_by_measure_q.c.avg_by_measure.desc().nullslast(),
            agg_by_measure_q.c.nb_mesures.desc(),
            agg_by_measure_q.c.id_arrondissement.asc(),
        )

    final_q = final_q.limit(top_n)
    results = final_q.all()

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


def _availability_by_arrondissement(db: Session):
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
        .order_by(func.coalesce((100.0 * active_expr / func.nullif(total_expr, 0)), 0).desc())
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


def _citizens_most_engaged(db: Session, limit: int = 20):
    rows = db.query(models.Citoyen).order_by(models.Citoyen.score_engagement.desc()).limit(limit).all()
    return [{"id_citoyen": r.id_citoyen, "nom": r.nom, "score_engagement": float(r.score_engagement or 0)} for r in rows]


def _predictive_this_month(db: Session):
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
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


@router.get("/pollution_24h")
def pollution_24h(pollutant: str = "PM2.5", top_n: int = 10, order_by: str = "measure", db: Session = Depends(get_db)):
    """
    Retourne les arrondissements les plus pollués sur les dernières 24h.
    Utilise uniquement des requêtes SQLAlchemy ORM (pas de SQL brut).
    """
    return _pollution_24h(db, pollutant=pollutant, top_n=top_n, order_by=order_by)


@router.get("/availability_by_arrondissement")
def availability_by_arrondissement(db: Session = Depends(get_db)):
    return _availability_by_arrondissement(db)


@router.get("/citizens_most_engaged")
def citizens_most_engaged(limit: int = 20, db: Session = Depends(get_db)):
    return _citizens_most_engaged(db, limit=limit)


@router.get("/predictive_this_month")
def predictive_this_month(db: Session = Depends(get_db)):
    return _predictive_this_month(db)


@router.get("/top_trajets")
def top_trajets(limit: int = 20, db: Session = Depends(get_db)):
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
    rows = q.all()
    out = []
    for r in rows:
        out.append({
            "id_trajet": r[0],
            "origine": r[1],
            "destination": r[2],
            "co2_economie": float(r[3]) if r[3] is not None else None
        })
    return out