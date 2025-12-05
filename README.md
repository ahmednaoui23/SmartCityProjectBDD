# SmartCityProjectBDD — Analyse fonctionnelle

Ce document présente l'analyse fonctionnelle du projet SmartCityProjectBDD telle qu'extraite du code source du dépôt (modèles SQLAlchemy, routers, main.py). Il décrit les objectifs applicatifs, les acteurs, les cas d'utilisation principaux, le modèle de données résumé, l'API exposée, les prérequis techniques et des recommandations pour la suite.

---

## 1. Contexte et objectifs

SmartCityProjectBDD est une API backend (FastAPI + SQLAlchemy) destinée à gérer les composants d'une "ville intelligente" centrée sur :
- le déploiement et la maintenance de capteurs (environnementaux, etc.),
- la collecte et la gestion des mesures issues des capteurs,
- la gestion d'interventions techniques et des techniciens associés,
- la participation citoyenne via des consultations publiques,
- le suivi des trajets et véhicules (indicateurs CO2),
- la gestion des propriétaires de capteurs.

L'implémentation utilise des types avancés (UUID, ENUM, JSON) et vise PostgreSQL comme SGBD recommandé.

---

## 2. Acteurs (rôles fonctionnels)
- Propriétaire (Proprietaire) : possesseur d'un ou plusieurs capteurs.
- Technicien (Technicien) : intervient sur des capteurs.
- Citoyen (Citoyen) : participe aux consultations publiques.
- Capteur (Capteur) : objet matériel produisant des mesures.
- Application / Service IA : peut proposer/valider des interventions (champ `Ia_valide`).
- ## 3. Cas d'utilisation principaux

1. Gestion des capteurs
   - Enregistrer, modifier, supprimer un capteur.
   - Affecter un capteur à un propriétaire et/ou un arrondissement.
   - Mettre à jour le statut d'un capteur.
   - Consulter l'historique des statuts.

2. Collecte et consultation des mesures
   - Recevoir et stocker des mesures horodatées (polluant, valeur, unité).
   - Interroger les séries temporelles par capteur, période ou polluant.

3. Gestion des interventions
   - Créer des interventions (préventive/corrective/curative) sur des capteurs.
   - Associer des techniciens à une intervention (avec rôle).
   - Calculer et enregistrer l'impact (ex. CO2).

4. Participation citoyenne
   - Créer et gérer des consultations publiques.
   - Enregistrer la participation des citoyens (avis, vote).
   - Suivre le score d'engagement des citoyens.

5. Mobilité & trajets
   - Enregistrer trajets liés à des véhicules (distance, durée, économies CO2).
   - Analyser historique de trajets par véhicule.

6. Administration géographique
   - Gérer les arrondissements et la répartition des capteurs.

---

## 4. Modèle de données (résumé conceptuel)

Les entités principales et attributs clés (issus du dossier `app/models`) :

- Arrondissement
  - id_arrondissement (PK int)
  - nom (varchar(100), unique)

- Proprietaire
  - id_proprietaire (PK bigint)
  - nom, adresse, telephone, email (unique), type_proprietaire

- Capteur
  - uuid_capteur (PK UUID)
  - type_capteur, latitude, longitude
  - statut (ENUM: active, maintenance, out_of_service, failed)
  - date_installation
  - id_proprietaire (FK -> proprietaire)
  - id_arrondissement (FK -> arrondissement)

- Mesure
  - id (PK bigint)
  - uuid_capteur (FK -> capteur) — ON DELETE CASCADE
  - ts, pollutant, valeur, unite

- CapteurStatusHistory
  - id (PK bigint)
  - uuid_capteur (FK -> capteur) — ON DELETE CASCADE
  - status (enum), ts

- Intervention
  - id_intervention (PK bigint)
  - date_heure, nature (enum), duree_minutes, cout, impact_co2, ia_valide
  - uuid_capteur (FK -> capteur)

- Technicien
  - id_technicien (PK bigint)
  - nom, telephone, certification

- Realiser (association Intervention <-> Technicien)
  - id_intervention (PK, FK)
  - id_technicien (PK, FK)
  - role

- Citoyen
  - id_citoyen (PK bigint)
  - nom, adresse, email, score_engagement, preferences_mobilite (JSON)

- Consultation
  - id_consultation (PK bigint)
  - titre, date_consultation, theme

- ParticiperA (association Citoyen <-> Consultation)
  - id_citoyen (PK, FK)
  - id_consultation (PK, FK)
  - avis, vote, date_participation

- Vehicule
  - plaque (PK varchar(20))
  - type_vehicule, energie

- Trajet
  - id_trajet (PK bigint)
  - origine, destination, distance_km, duree_minutes, co2_economie, date_heure
  - plaque (FK -> vehicule)

Remarque : Les cardinalités principales (1:N, N:N via tables d'association) sont déduites des relationships SQLAlchemy.
## 5. API — points d'accès (dérivé de main.py)

Le fichier `main.py` inclut les routers suivants avec leurs préfixes :

- /api/proprietaires  (router: proprietaire)
- /api/capteurs       (router: capteur)
- /api/mesures        (router: mesure)
- /api/techniciens    (router: technicien)
- /api/interventions  (router: intervention)
- /api/realisers      (router: realiser)
- /api/citoyens       (router: citoyen)
- /api/consultations  (router: consultation)
- /api/participations (router: participer_a)
- /api/vehicules      (router: vehicule)
- /api/trajets        (router: trajet)
- /api/analytics      (router: analytics)

Note : Les routes précises (méthodes CRUD, paramètres) sont définies dans chaque module de `app/routers`. Pour une documentation complète, lancer l'application et consulter l'OpenAPI Swagger : `/docs`.

---

## 6. Analytics - Pollution 24h Metrics

### Overview

The `pollution_24h` endpoint provides pollution analytics by arrondissement for the last 24 hours, with enhanced filtering and dual-metric calculation.

### Features

- **Active Sensor Filtering**: Only includes sensors considered active based on:
  - Latest entry in `capteur_status_history` (if present)
  - Falls back to `capteur.statut` if no history exists
  - Only sensors with status = 'active' are included

- **Dual Metrics**:
  - `avg_by_measure`: Average of all measurement values across all active sensors
  - `avg_by_sensor`: Average of per-sensor averages (each sensor has equal weight)
  - Both metrics are rounded to 2 decimal places

- **Transparency**: Returns `nb_mesures` (count of measurements) and `nb_capteurs` (count of sensors) for each arrondissement

### Parameters

- `pollutant` (string, default: 'PM2.5'): Type of pollutant to analyze (e.g., 'PM2.5', 'PM10', 'NO2', 'O3')
- `top_n` (integer, default: 10): Maximum number of arrondissements to return

### Usage Examples

```python
# Get top 10 arrondissements by PM2.5 pollution
GET /api/analytics/pollution_24h

# Get top 5 arrondissements by PM10 pollution
GET /api/analytics/pollution_24h?pollutant=PM10&top_n=5
```

### Response Format

```json
[
  {
    "id_arrondissement": 1,
    "nom": "Arrondissement 1",
    "avg_by_measure": 25.67,
    "avg_by_sensor": 26.45,
    "nb_capteurs": 15,
    "nb_mesures": 450
  },
  ...
]
```

### Understanding the Metrics

- **avg_by_measure**: Treats all measurements equally. If one sensor produces 100 measurements and another produces 10, the first sensor has more influence on the average. This represents the overall pollution level considering all data points.

- **avg_by_sensor**: Each sensor contributes equally to the average, regardless of how many measurements it produced. This provides a more balanced view when sensors have varying measurement frequencies.

Example:
- Sensor A: measurements [10, 20] → avg = 15
- Sensor B: measurements [30, 40] → avg = 35
- avg_by_measure = (10 + 20 + 30 + 40) / 4 = 25.0
- avg_by_sensor = (15 + 35) / 2 = 25.0

### Performance Optimization

#### Recommended Indexes

Run the provided SQL scripts to create performance indexes:

```bash
psql -d smart_city -f scripts/create_indexes.sql
```

This creates indexes on:
- `mesure(pollutant, ts)` - Speeds up pollutant and time range filtering
- `mesure(uuid_capteur, ts)` - Speeds up per-sensor queries
- `capteur(id_arrondissement)` - Speeds up arrondissement grouping
- `capteur_status_history(uuid_capteur, ts DESC)` - Speeds up latest status lookups

#### Materialized View

For even better performance with frequently-run queries, use the materialized view:

```bash
psql -d smart_city -f scripts/create_mv_pollution_24h.sql
```

**Refreshing the materialized view**:

```sql
-- Standard refresh (locks the view)
REFRESH MATERIALIZED VIEW mv_pollution_24h_active;

-- Concurrent refresh (requires unique index, no locks)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_pollution_24h_active;
```

**Querying the materialized view**:

```sql
SELECT * FROM mv_pollution_24h_active 
WHERE pollutant = 'PM2.5' 
ORDER BY avg_by_measure DESC 
LIMIT 10;
```

**Automated refresh with pg_cron** (optional):

```sql
-- Refresh every 15 minutes
SELECT cron.schedule('refresh-pollution-view', '*/15 * * * *', 
  'REFRESH MATERIALIZED VIEW mv_pollution_24h_active');
```

---

## 7. Testing

### Running Tests

The project includes unit tests for analytics functions. To run tests:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_analytics_pollution.py -v

# Run with PostgreSQL (requires TEST_WITH_POSTGRES=true)
TEST_WITH_POSTGRES=true pytest tests/test_analytics_pollution.py -v
```

### Test Coverage

- `test_pollution_24h_basic`: Verifies basic functionality with seeded data
- `test_pollution_24h_exclude_inactive`: Ensures inactive sensors are properly excluded
- `test_pollution_24h_different_pollutant`: Tests pollutant filtering
- `test_pollution_24h_top_n_limit`: Validates the top_n parameter

**Note**: Analytics tests require PostgreSQL as they use PostgreSQL-specific SQL features (intervals, COALESCE, etc.). Set `TEST_WITH_POSTGRES=true` and provide a `TEST_DATABASE_URL` to run them.

---

## 8. Pré-requis techniques & exécution

- Python 3.10+ recommandé.
- SGBD : PostgreSQL (recommandé). Les modèles utilisent UUID/ENUM/JSON.
- Dépendances : voir `requirements.txt`.
- Variables d'environnement : voir `.env.examples`.
- Commandes de démarrage (développement) :
  - Installer deps : `pip install -r requirements.txt`
  - Configurer la base (URL dans ENV)
  - Lancer : `uvicorn main:app --reload`

