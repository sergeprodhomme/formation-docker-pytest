"""Couche d'acces aux donnees.

Deux modes :
- DATABASE_URL present (conteneur docker-compose) : vraie base PostgreSQL.
- DATABASE_URL absent (tests locaux) : simulacre en memoire, pour que la
  suite pytest reste executable sans service.

Le module ne contient AUCUNE logique de hachage : il delegue a security.py
(cf. create_utilisateur) et recoit deja les haches prets a inserer.
"""

import os

# ------------------------------------------------------------------
# Mode sans base : simulacre en memoire (comme avant).
# ------------------------------------------------------------------
_FAKE_DB = {
    1: {"name": "Alice"},
    2: {"name": "Bob"},
}

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_user(user_id: int) -> dict | None:
    return _FAKE_DB.get(user_id)


# ------------------------------------------------------------------
# Mode PostgreSQL : connecte a la base montee par docker compose.
# ------------------------------------------------------------------
def _get_connection():
    import psycopg2  # import paresseux : pas besoin dans les tests unitaires

    return psycopg2.connect(
        DATABASE_URL,
        # Ne pas rester bloque indefiniment si la base ne repond pas.
        connect_timeout=5,
        # Identifie l'application cote serveur (utile dans pg_stat_activity).
        application_name="pytest-formation",
    )


def create_utilisateur(
    nom: str,
    prenom: str,
    courriel: str,
    courriel_hash: str,
    numero_rpps: str,
    mot_de_passe_hash: str,
) -> dict:
    """Insere un utilisateur dont les haches sont DEJA calculees.

    On passe les haches en arguments plutot qu'en clair le mot de passe :
    la couche acces donnees ne doit connaitre que des donnees pretes.
    """
    with _get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO utilisateurs
                (nom, prenom, courriel, courriel_hash, numero_rpps, mot_de_passe_hash)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, nom, prenom, courriel, numero_rpps,
                      courriel_hash, mot_de_passe_hash, cree_le
            """,
            (nom, prenom, courriel, courriel_hash, numero_rpps, mot_de_passe_hash),
        )
        cols = [d.name for d in cur.description]
        row = cur.fetchone()
    return dict(zip(cols, row))


def get_utilisateur_by_courriel(courriel: str) -> dict | None:
    """Recherche PSEUDONYMISEE : on interroge par le hache HMAC du courriel,
    jamais par l'adresse en clair."""
    from security import hash_email

    with _get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, nom, prenom, courriel, numero_rpps, mot_de_passe_hash "
            "FROM utilisateurs WHERE courriel_hash = %s",
            (hash_email(courriel),),
        )
        cols = [d.name for d in cur.description]
        row = cur.fetchone()
    return dict(zip(cols, row)) if row else None
