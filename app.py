"""Code applicatif minimal à tester."""

import database
import security


def add(a: float, b: float) -> float:
    return a + b


def slugify(text: str) -> str:
    return text.strip().lower().replace(" ", "-")


def fetch_user(user_id: int) -> str | None:
    """Depend d'une source externe (ici un suppositoire de BDD).

    C'est le candidat ideal pour etre mocke dans les tests.
    """
    user = database.get_user(user_id)
    if user is None:
        return None
    return user["name"].title()


# ------------------------------------------------------------------
# Creation de compte : orchestre validation, hachage, insertion.
# ------------------------------------------------------------------

def _valider_numero_rpps(numero_rpps: str) -> str:
    """Le RPPS est un numero de praticien de 11 chiffres."""
    if not (len(numero_rpps) == 11 and numero_rpps.isdigit()):
        raise ValueError("numero RPPS invalide : 11 chiffres attendus")
    return numero_rpps


def register_utilisateur(
    nom: str,
    prenom: str,
    courriel: str,
    numero_rpps: str,
    mot_de_passe: str,
    mot_de_passe_confirmation: str | None = None,
) -> dict:
    """Cree un compte utilisateur complet.

    Etapes :
    1. Validations metier (RPPS, confirmation du mot de passe).
    2. Hachages : bcrypt pour le mot de passe, HMAC pour le courriel.
    3. Insertion via la couche acces donnees (moquable dans les tests).
    """
    _valider_numero_rpps(numero_rpps)

    if mot_de_passe_confirmation is not None and mot_de_passe != mot_de_passe_confirmation:
        raise ValueError("le mot de passe et sa confirmation different")

    return database.create_utilisateur(
        nom=nom.strip(),
        prenom=prenom.strip(),
        courriel=courriel.strip(),
        courriel_hash=security.hash_email(courriel),
        numero_rpps=numero_rpps,
        mot_de_passe_hash=security.hash_password(mot_de_passe),
    )


def authenticate(courriel: str, mot_de_passe: str) -> dict | None:
    """Connexion : retrouve par hache de courriel, verifie bcrypt."""
    utilisateur = database.get_utilisateur_by_courriel(courriel)
    if utilisateur is None:
        return None
    if not security.verify_password(mot_de_passe, utilisateur["mot_de_passe_hash"]):
        return None
    return utilisateur
