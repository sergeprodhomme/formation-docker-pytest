#!/bin/bash
# Compte applicatif au moindre privilege.
# Execute au PREMIER demarrage par docker-entrypoint.sh, avec toutes les
# variables du service db dans l'environnement (dont $POSTGRES_APP_PASSWORD).
# EOSQL est SANS quotes pour que le shell expande la variable ci-dessous.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOSQL
    CREATE ROLE appuser LOGIN PASSWORD '$POSTGRES_APP_PASSWORD';

    GRANT SELECT, INSERT, UPDATE, DELETE
        ON ALL TABLES IN SCHEMA public TO appuser;

    -- Indispensable pour les colonnes SERIAL : l'INSERT avance la sequence.
    GRANT USAGE, SELECT
        ON ALL SEQUENCES IN SCHEMA public TO appuser;

    ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO appuser;

    ALTER DEFAULT PRIVILEGES IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO appuser;
EOSQL

echo ">>> appuser cree et privileges accordes."
