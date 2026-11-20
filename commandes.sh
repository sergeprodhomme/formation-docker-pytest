#!/bin/sh
# Commandes verifiees de la session (base PostgreSQL + appuser + .env).

# --- Tout reconstruire de zero (schema + rôles) ---
docker compose down -v
docker compose up -d --build
docker compose logs db | grep -E "01-schema|appuser"   # verifier les scripts d'init

# --- Peupler la base ---
docker compose run --rm web python seed.py

# --- Lancer les tests (19) en conteneur ---
docker compose run --rm web            # CMD = pytest -v
docker run --rm my-pytest-app          # variante sans base (fake DB en memoire)

# --- Inspecter la base ---
docker compose exec db psql -U user -d testdb          # super-utilisateur
docker compose exec db psql -U appuser -d testdb       # compte applicatif
#   \dt  \d utilisateurs  SELECT * FROM utilisateurs;  \q

# --- Verifier le moindre privilege (doit echouer) ---
docker compose exec db psql -U appuser -d testdb -c "CREATE TABLE test(x int);"
#   attendu : ERROR: permission denied for schema public

# --- Sauvegarde / restauration ---
docker compose exec db pg_dump -U user testdb > backup_$(date +%F).sql
docker compose exec db psql -U user -d testdb -c "DROP TABLE utilisateurs;"   # simulation d'incident
docker compose exec -T db psql -U user -d testdb < backup_$(date +%F).sql
rm backup_$(date +%F).sql     # contient des donnees : supprimer apres usage

# --- Outils ---
# GUI du Mac : hote 127.0.0.1, port 15432, base testdb (voir .env)
docker compose exec db psql -U user -d testdb -c "SELECT query, calls FROM pg_stat_statements ORDER BY calls DESC LIMIT 5;"

# --- Rappel secrets ---
# Tout est dans .env (NON committe) : POSTGRES_PASSWORD, POSTGRES_APP_PASSWORD, DATABASE_URL, SECRET_HMAC
