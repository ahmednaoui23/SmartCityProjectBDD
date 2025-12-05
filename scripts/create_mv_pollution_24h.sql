-- Materialized View for Pollution 24h Analytics with Active Sensors
-- This materialized view pre-computes pollution metrics for the last 24 hours,
-- filtering only active sensors based on capteur_status_history or capteur.statut

-- Drop existing view if it exists
DROP MATERIALIZED VIEW IF EXISTS mv_pollution_24h_active;

-- Create materialized view
CREATE MATERIALIZED VIEW mv_pollution_24h_active AS
WITH last_status AS (
  SELECT DISTINCT ON (uuid_capteur) uuid_capteur, status
  FROM capteur_status_history
  ORDER BY uuid_capteur, ts DESC
),
active_sensors AS (
  SELECT c.uuid_capteur
  FROM capteur c
  LEFT JOIN last_status ls ON c.uuid_capteur = ls.uuid_capteur
  WHERE COALESCE(ls.status, c.statut) = 'active'
),
measures_24h AS (
  SELECT m.uuid_capteur, m.valeur, c.id_arrondissement, m.pollutant
  FROM mesure m
  JOIN active_sensors acs ON m.uuid_capteur = acs.uuid_capteur
  JOIN capteur c ON m.uuid_capteur = c.uuid_capteur
  WHERE m.ts >= now() - interval '24 hours'
),
sensor_averages AS (
  SELECT id_arrondissement, pollutant, uuid_capteur, AVG(valeur) as sensor_avg
  FROM measures_24h
  GROUP BY id_arrondissement, pollutant, uuid_capteur
)
SELECT 
  a.id_arrondissement,
  a.nom,
  m.pollutant,
  ROUND(AVG(m.valeur)::numeric, 2) AS avg_by_measure,
  ROUND(AVG(sa.sensor_avg)::numeric, 2) AS avg_by_sensor,
  COUNT(DISTINCT m.uuid_capteur)::int AS nb_capteurs,
  COUNT(m.valeur)::int AS nb_mesures,
  now() AS refreshed_at
FROM measures_24h m
JOIN arrondissement a ON m.id_arrondissement = a.id_arrondissement
JOIN sensor_averages sa ON m.id_arrondissement = sa.id_arrondissement 
  AND m.pollutant = sa.pollutant
GROUP BY a.id_arrondissement, a.nom, m.pollutant;

-- Create index on the materialized view for efficient querying
CREATE INDEX IF NOT EXISTS idx_mv_pollution_24h_active_pollutant 
ON mv_pollution_24h_active(pollutant);

CREATE INDEX IF NOT EXISTS idx_mv_pollution_24h_active_arr 
ON mv_pollution_24h_active(id_arrondissement);

-- ============================================================
-- HOW TO REFRESH THE MATERIALIZED VIEW
-- ============================================================
-- 
-- The materialized view needs to be refreshed periodically to get updated data.
-- Run one of the following commands:
--
-- 1. Standard refresh (locks the view during refresh):
--    REFRESH MATERIALIZED VIEW mv_pollution_24h_active;
--
-- 2. Concurrent refresh (allows queries during refresh, requires unique index):
--    First create a unique index:
--    CREATE UNIQUE INDEX idx_mv_pollution_24h_active_unique 
--    ON mv_pollution_24h_active(id_arrondissement, pollutant);
--    
--    Then refresh concurrently:
--    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_pollution_24h_active;
--
-- 3. Automated refresh using cron or pg_cron extension:
--    Example using pg_cron (requires extension):
--    SELECT cron.schedule('refresh-pollution-view', '*/15 * * * *', 
--      'REFRESH MATERIALIZED VIEW mv_pollution_24h_active');
--
-- ============================================================
-- USAGE EXAMPLES
-- ============================================================
--
-- Query all pollutants for top 10 arrondissements:
-- SELECT * FROM mv_pollution_24h_active 
-- WHERE pollutant = 'PM2.5' 
-- ORDER BY avg_by_measure DESC 
-- LIMIT 10;
--
-- Check when the view was last refreshed:
-- SELECT MAX(refreshed_at) FROM mv_pollution_24h_active;
