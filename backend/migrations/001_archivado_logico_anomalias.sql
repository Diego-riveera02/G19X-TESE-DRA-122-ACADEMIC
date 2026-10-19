-- PluriOne: archivado logico de anomalias.
-- No elimina ni modifica registros existentes.
-- Los registros actuales permanecen activos.

BEGIN;

SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '30s';

ALTER TABLE anomaly_logs
    ADD COLUMN archived BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN archived_at TIMESTAMPTZ NULL;

COMMIT;
