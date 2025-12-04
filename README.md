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

## 6. Pré-requis techniques & exécution

- Python 3.10+ recommandé.
- SGBD : PostgreSQL (recommandé). Les modèles utilisent UUID/ENUM/JSON.
- Dépendances : voir `requirements.txt`.
- Variables d'environnement : voir `.env.examples`.
- Commandes de démarrage (développement) :
  - Installer deps : `pip install -r requirements.txt`
  - Configurer la base (URL dans ENV)
  - Lancer : `uvicorn main:app --reload`

