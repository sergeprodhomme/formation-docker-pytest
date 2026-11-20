"""Fonctions de hachage : mots de passe (bcrypt) et courriel (HMAC-SHA256).

Pourquoi deux hachages differents ?

- Le mot de passe doit etre IRRVERSIBLE et LENT : bcrypt (sel aleatoire
  integre au hache, facteur de cout). On ne le re-verifie qu'a la connexion.
- Le courriel doit rester RECHERCHABLE : on veut retrouver un compte par
  son adresse sans la stocker en clair dans les index. Un HMAC-SHA256
  (cle secrete serveur) est rapide et deterministe, ce qu'on veut ici,
  mais il ne serait JAMAIS acceptable pour un mot de passe.
"""

import hashlib
import hmac
import os

import bcrypt

# Cle HMAC : en production, la passer par une variable d'environnement
# (SECRET_HMAC dans docker-compose.yml). Valeur par defaut pour la formation.
SECRET_HMAC = os.environ.get("SECRET_HMAC", "cle-secrete-a-remplacer-en-production")


def hash_password(password: str) -> str:
    """Retourne un hache bcrypt, ex. $2b$12$... (60 caracteres)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, mot_de_passe_hash: str) -> bool:
    """Compare en temps constant ; bcrypt extrait le sel du hache stocke."""
    return bcrypt.checkpw(password.encode("utf-8"), mot_de_passe_hash.encode("utf-8"))


def normalize_email(courriel: str) -> str:
    """Normalisation avant hachage : minuscules, sans espaces.

    Sans cais, 'Alice@Exemple.COM' et 'alice@example.com' donneraient
    deux haches differents pour la meme personne.
    """
    return courriel.strip().lower()


def hash_email(courriel: str, secret: str = SECRET_HMAC) -> str:
    """HMAC-SHA256 hexadecimal (64 caracteres) du courriel normalise."""
    return hmac.new(
        secret.encode("utf-8"),
        normalize_email(courriel).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
