from fastapi import FastAPI
from app.database import engine, Base
# Assurer l'import des modèles pour que SQLAlchemy crée les tables
import app.models  # noqa: F401

# Import des routers
from app.models import (
    proprietaire,
    capteur,
    mesure,
    technicien,
    intervention,
    realiser,
    citoyen,
    consultation,
    participer_a,
    vehicule,
    trajet,
    arrondissement,
    capteur_status_history
)

# Création de l'application FastAPI
app = FastAPI(title="Smart City Analytics API - Complete Backend")

# Création des tables dans la base (à utiliser uniquement en développement)
Base.metadata.create_all(bind=engine)

# Inclusion des routers avec leurs préfixes et tags
app.include_router(proprietaire.router, prefix="/api/proprietaires", tags=["proprietaires"])
app.include_router(capteur.router, prefix="/api/capteurs", tags=["capteurs"])
app.include_router(mesure.router, prefix="/api/mesures", tags=["mesures"])
app.include_router(technicien.router, prefix="/api/techniciens", tags=["techniciens"])
app.include_router(intervention.router, prefix="/api/interventions", tags=["interventions"])
app.include_router(realiser.router, prefix="/api/realisers", tags=["realisers"])
app.include_router(citoyen.router, prefix="/api/citoyens", tags=["citoyens"])
app.include_router(consultation.router, prefix="/api/consultations", tags=["consultations"])
app.include_router(participer_a.router, prefix="/api/participations", tags=["participations"])
app.include_router(vehicule.router, prefix="/api/vehicules", tags=["vehicules"])
app.include_router(trajet.router, prefix="/api/trajets", tags=["trajets"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

# Endpoint racine pour vérifier que le serveur fonctionne
@app.get("/")
def root():
    return {"service": "Smart City Analytics API", "status": "ok"}

