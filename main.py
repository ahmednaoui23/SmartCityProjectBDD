from fastapi import FastAPI, Request
from app.database import engine, Base
# Assurer l'import des modèles pour que SQLAlchemy crée les tables
import app.models  # noqa: F401

# Import des routers
from app.routers import (
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
    analytics,
)

app = FastAPI(title="Smart City Analytics API - Complete Backend")

# Création des tables dans la base (à utiliser uniquement en développement)
Base.metadata.create_all(bind=engine)

# Middleware pour supprimer l'en-tête Content-Type des réponses
@app.middleware("http")
async def remove_content_type_header(request: Request, call_next):
    response = await call_next(request)
    # supprimer l'en-tête content-type si présent
    if "content-type" in response.headers:
        del response.headers["content-type"]
    return response


app.include_router(proprietaire.router, prefix="/proprietaires", tags=["proprietaires"])
app.include_router(capteur.router, prefix="/capteurs", tags=["capteurs"])
app.include_router(mesure.router, prefix="/mesures", tags=["mesures"])
app.include_router(technicien.router, prefix="/techniciens", tags=["techniciens"])
app.include_router(intervention.router, prefix="/interventions", tags=["interventions"])
app.include_router(realiser.router, prefix="/realisers", tags=["realisers"])
app.include_router(citoyen.router, prefix="/citoyens", tags=["citoyens"])
app.include_router(consultation.router, prefix="/consultations", tags=["consultations"])
app.include_router(participer_a.router, prefix="/participations", tags=["participations"])
app.include_router(vehicule.router, prefix="/vehicules", tags=["vehicules"])
app.include_router(trajet.router, prefix="/trajets", tags=["trajets"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


@app.get("/")
def root():
    return {"service": "Smart City Analytics API", "status": "ok"}