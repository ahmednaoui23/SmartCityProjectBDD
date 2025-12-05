-- Performance Indexes for Pollution Analytics
-- These indexes optimize the pollution_24h query and related analytics

-- Index on mesure for pollutant and timestamp filtering
-- Supports efficient filtering by pollutant type and time range
CREATE INDEX IF NOT EXISTS idx_mesure_pollutant_ts 
ON mesure(pollutant, ts);

-- Index on mesure for sensor-based queries with timestamp
-- Supports efficient joins with capteur and time-based filtering
CREATE INDEX IF NOT EXISTS idx_mesure_uuid_capteur_ts 
ON mesure(uuid_capteur, ts);

-- Index on capteur for arrondissement-based grouping
-- Supports efficient joins with arrondissement table
CREATE INDEX IF NOT EXISTS idx_capteur_id_arrondissement 
ON capteur(id_arrondissement);

-- Optional: Composite index for capteur status queries
-- Improves performance when filtering by status
CREATE INDEX IF NOT EXISTS idx_capteur_statut 
ON capteur(statut);

-- Optional: Index on capteur_status_history for latest status lookups
-- Supports the DISTINCT ON query for finding latest status per sensor
CREATE INDEX IF NOT EXISTS idx_capteur_status_history_uuid_ts 
ON capteur_status_history(uuid_capteur, ts DESC);

-- To verify indexes have been created:
-- \di idx_mesure_pollutant_ts
-- \di idx_mesure_uuid_capteur_ts
-- \di idx_capteur_id_arrondissement
