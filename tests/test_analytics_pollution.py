"""
Unit tests for pollution analytics (pollution_24h function).

Tests verify:
- Basic functionality with seeded data
- Exclusion of inactive sensors
- Proper calculation of avg_by_measure and avg_by_sensor
- Filtering by pollutant type

Note: These tests use an in-memory SQLite database for simplicity.
The pollution_24h function uses PostgreSQL-specific SQL (intervals, COALESCE, etc.)
which may not work identically in SQLite. For production testing with PostgreSQL,
use a test database with PostgreSQL and adjust the SQL query accordingly.
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4
import os

# Check if we should use PostgreSQL for testing
USE_POSTGRES = os.getenv("TEST_WITH_POSTGRES", "false").lower() == "true"

if USE_POSTGRES:
    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:admin123@localhost:5432/smart_city_test")
else:
    TEST_DATABASE_URL = "sqlite:///:memory:"

from app.database import Base
from app import crud, models


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    Uses in-memory SQLite by default, or PostgreSQL if TEST_WITH_POSTGRES=true.
    """
    if not USE_POSTGRES:
        pytest.skip("These tests require PostgreSQL. Set TEST_WITH_POSTGRES=true to run them.")

    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()
    try:
        yield session
        session.rollback()  # Rollback any changes
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_pollution_24h_basic(db_session):
    """
    Test basic pollution_24h functionality with seeded data.
    Verifies that both avg_by_measure and avg_by_sensor are calculated correctly.
    """
    # Create arrondissement
    arr1 = models.Arrondissement(id_arrondissement=1, nom="Arrondissement 1")
    db_session.add(arr1)
    db_session.commit()

    # Create 2 active sensors
    sensor1_uuid = uuid4()
    sensor2_uuid = uuid4()

    sensor1 = models.Capteur(
        uuid_capteur=sensor1_uuid,
        type_capteur="air_quality",
        statut=models.capteur.CapteurStatusEnum.active,
        id_arrondissement=1
    )
    sensor2 = models.Capteur(
        uuid_capteur=sensor2_uuid,
        type_capteur="air_quality",
        statut=models.capteur.CapteurStatusEnum.active,
        id_arrondissement=1
    )
    db_session.add(sensor1)
    db_session.add(sensor2)
    db_session.commit()

    # Create measures for the last 24 hours
    # Sensor 1: values [10.0, 20.0] -> avg = 15.0
    # Sensor 2: values [30.0, 40.0] -> avg = 35.0
    # avg_by_measure: (10+20+30+40)/4 = 25.0
    # avg_by_sensor: (15.0+35.0)/2 = 25.0

    now = datetime.utcnow()

    measures = [
        models.Mesure(uuid_capteur=sensor1_uuid, ts=now - timedelta(hours=1),
                      pollutant="PM2.5", valeur=10.0, unite="µg/m³"),
        models.Mesure(uuid_capteur=sensor1_uuid, ts=now - timedelta(hours=2),
                      pollutant="PM2.5", valeur=20.0, unite="µg/m³"),
        models.Mesure(uuid_capteur=sensor2_uuid, ts=now - timedelta(hours=1),
                      pollutant="PM2.5", valeur=30.0, unite="µg/m³"),
        models.Mesure(uuid_capteur=sensor2_uuid, ts=now - timedelta(hours=2),
                      pollutant="PM2.5", valeur=40.0, unite="µg/m³"),
    ]

    for m in measures:
        db_session.add(m)
    db_session.commit()

    # Call pollution_24h
    results = crud.pollution_24h(db_session, pollutant="PM2.5", top_n=10)

    # Verify results
    assert len(results) == 1
    row = results[0]

    assert row[0] == 1  # id_arrondissement
    assert row[1] == "Arrondissement 1"  # nom
    assert row[2] == 25.0  # avg_by_measure
    assert row[3] == 25.0  # avg_by_sensor
    assert row[4] == 2  # nb_capteurs
    assert row[5] == 4  # nb_mesures


def test_pollution_24h_exclude_inactive(db_session):
    """
    Test that inactive sensors are excluded from pollution_24h results.
    A sensor with last status != 'active' should not influence the result.
    """
    # Create arrondissement
    arr1 = models.Arrondissement(id_arrondissement=1, nom="Arrondissement 1")
    db_session.add(arr1)
    db_session.commit()

    # Create 2 sensors: one active, one inactive
    sensor_active = uuid4()
    sensor_inactive = uuid4()

    s1 = models.Capteur(
        uuid_capteur=sensor_active,
        type_capteur="air_quality",
        statut=models.capteur.CapteurStatusEnum.active,
        id_arrondissement=1
    )
    s2 = models.Capteur(
        uuid_capteur=sensor_inactive,
        type_capteur="air_quality",
        statut=models.capteur.CapteurStatusEnum.active,  # Initially active
        id_arrondissement=1
    )
    db_session.add(s1)
    db_session.add(s2)
    db_session.commit()

    # Add status history to mark sensor 2 as inactive
    now = datetime.utcnow()
    status_history = models.CapteurStatusHistory(
        uuid_capteur=sensor_inactive,
        status=models.capteur.CapteurStatusEnum.maintenance,
        ts=now - timedelta(hours=1)
    )
    db_session.add(status_history)
    db_session.commit()

    # Add measures for both sensors
    # Active sensor: values [10.0, 20.0] -> avg = 15.0
    # Inactive sensor: values [100.0, 200.0] -> should be excluded

    measures = [
        models.Mesure(uuid_capteur=sensor_active, ts=now - timedelta(hours=1),
                      pollutant="PM2.5", valeur=10.0, unite="µg/m³"),
        models.Mesure(uuid_capteur=sensor_active, ts=now - timedelta(hours=2),
                      pollutant="PM2.5", valeur=20.0, unite="µg/m³"),
        models.Mesure(uuid_capteur=sensor_inactive, ts=now - timedelta(hours=1),
                      pollutant="PM2.5", valeur=100.0, unite="µg/m³"),
        models.Mesure(uuid_capteur=sensor_inactive, ts=now - timedelta(hours=2),
                      pollutant="PM2.5", valeur=200.0, unite="µg/m³"),
    ]

    for m in measures:
        db_session.add(m)
    db_session.commit()

    # Call pollution_24h
    results = crud.pollution_24h(db_session, pollutant="PM2.5", top_n=10)

    # Verify results - only the active sensor should be included
    assert len(results) == 1
    row = results[0]

    assert row[0] == 1  # id_arrondissement
    assert row[1] == "Arrondissement 1"  # nom
    assert row[2] == 15.0  # avg_by_measure (only from active sensor)
    assert row[3] == 15.0  # avg_by_sensor (only from active sensor)
    assert row[4] == 1  # nb_capteurs (only 1 active sensor)
    assert row[5] == 2  # nb_mesures (only 2 measures from active sensor)


def test_pollution_24h_different_pollutant(db_session):
    """
    Test pollution_24h with a different pollutant type.
    Verifies the pollutant filter parameter works correctly.
    """
    # Create arrondissement
    arr1 = models.Arrondissement(id_arrondissement=1, nom="Arrondissement 1")
    db_session.add(arr1)
    db_session.commit()

    # Create active sensor
    sensor_uuid = uuid4()
    sensor = models.Capteur(
        uuid_capteur=sensor_uuid,
        type_capteur="air_quality",
        statut=models.capteur.CapteurStatusEnum.active,
        id_arrondissement=1
    )
    db_session.add(sensor)
    db_session.commit()

    # Add measures for PM10 and PM2.5
    now = datetime.utcnow()
    measures = [
        models.Mesure(uuid_capteur=sensor_uuid, ts=now - timedelta(hours=1),
                      pollutant="PM10", valeur=50.0, unite="µg/m³"),
        models.Mesure(uuid_capteur=sensor_uuid, ts=now - timedelta(hours=2),
                      pollutant="PM10", valeur=60.0, unite="µg/m³"),
        models.Mesure(uuid_capteur=sensor_uuid, ts=now - timedelta(hours=1),
                      pollutant="PM2.5", valeur=10.0, unite="µg/m³"),
    ]

    for m in measures:
        db_session.add(m)
    db_session.commit()

    # Query for PM10
    results = crud.pollution_24h(db_session, pollutant="PM10", top_n=10)

    # Verify only PM10 data is returned
    assert len(results) == 1
    row = results[0]

    assert row[2] == 55.0  # avg_by_measure (50+60)/2
    assert row[3] == 55.0  # avg_by_sensor
    assert row[5] == 2  # nb_mesures (only 2 PM10 measures)


def test_pollution_24h_top_n_limit(db_session):
    """
    Test that top_n parameter correctly limits the number of results.
    """
    # Create 3 arrondissements
    for i in range(1, 4):
        arr = models.Arrondissement(id_arrondissement=i, nom=f"Arrondissement {i}")
        db_session.add(arr)
    db_session.commit()

    # Create sensors and measures for each arrondissement
    now = datetime.utcnow()
    for i in range(1, 4):
        sensor_uuid = uuid4()
        sensor = models.Capteur(
            uuid_capteur=sensor_uuid,
            type_capteur="air_quality",
            statut=models.capteur.CapteurStatusEnum.active,
            id_arrondissement=i
        )
        db_session.add(sensor)
        db_session.commit()

        # Add measure with different values for each arrondissement
        measure = models.Mesure(
            uuid_capteur=sensor_uuid,
            ts=now - timedelta(hours=1),
            pollutant="PM2.5",
            valeur=float(i * 10),
            unite="µg/m³"
        )
        db_session.add(measure)
    db_session.commit()

    # Query with top_n=2
    results = crud.pollution_24h(db_session, pollutant="PM2.5", top_n=2)

    # Should return only 2 arrondissements (with highest avg_by_measure)
    assert len(results) == 2
    # Results should be ordered by avg_by_measure DESC
    assert results[0][2] >= results[1][2]
