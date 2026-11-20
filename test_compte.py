"""Tests de creation de compte : hachages, validation, orchestration.

Les hachages eux-memes (security.py) sont purs : on les teste reellement.
L'acces base (database.create_utilisateur) est moque, comme dans
test_app.py : ces tests ne dependent pas de PostgreSQL.
"""

import re

import pytest

import app
import security
import database


# ---------------------------------------------------------------
# security.py : les haches ont les bonnes proprietes
# ---------------------------------------------------------------

def test_hash_password_format_bcrypt():
    h = security.hash_password("s3cret!")
    # bcrypt : $2b$<cout>$<22 car. de sel><31 car. de hache>
    assert re.fullmatch(r"\$2b\$\d{2}\$[./A-Za-z0-9]{53}", h)


def test_hash_password_avec_sel_unique():
    # Deux appels avec le meme mot de passe => deux haches differents :
    # c'est le sel aleatoire integre par bcrypt.
    assert security.hash_password("abc") != security.hash_password("abc")


def test_verify_password():
    h = security.hash_password("s3cret!")
    assert security.verify_password("s3cret!", h)
    assert not security.verify_password("mauvais", h)


def test_hash_email_deterministe_et_normalise():
    a = security.hash_email("  Alice@EXAMPLE.COM ")
    b = security.hash_email("alice@example.com")
    assert a == b                      # normalisation avant hachage
    assert re.fullmatch(r"[0-9a-f]{64}", a)


def test_hash_email_change_avec_la_cle():
    assert security.hash_email("a@b.fr", secret="k1") != security.hash_email("a@b.fr", secret="k2")


# ---------------------------------------------------------------
# app.register_utilisateur : orchestration, base moquee
# ---------------------------------------------------------------

@pytest.fixture
def utilisateurs_enregistres(mocker):
    """Remplace l'acces base par une fausse table en memoire."""
    table = {}
    compteur = iter(range(1, 1000))

    def faux_create(nom, prenom, courriel, courriel_hash, numero_rpps, mot_de_passe_hash):
        utilisateur = {
            "id": next(compteur),
            "nom": nom, "prenom": prenom, "courriel": courriel,
            "courriel_hash": courriel_hash,
            "numero_rpps": numero_rpps,
            "mot_de_passe_hash": mot_de_passe_hash,
        }
        table[courriel_hash] = utilisateur
        return utilisateur

    mocker.patch("database.create_utilisateur", side_effect=faux_create)
    return table


def test_register_utilisateur_stocke_des_haches_pas_de_clair(mocker, utilisateurs_enregistres):
    app.register_utilisateur(
        nom="  Dupont  ", prenom="Alice", courriel="alice@example.fr",
        numero_rpps="10100317681", mot_de_passe="Mdp_2024!",
    )
    utilisateur = next(iter(utilisateurs_enregistres.values()))

    assert utilisateur["mot_de_passe_hash"].startswith("$2b$")
    assert "Mdp_2024!" not in str(utilisateur)     # rien en clair cote base
    assert len(utilisateur["courriel_hash"]) == 64
    assert utilisateur["nom"] == "Dupont"          # trimmed


def test_register_utilisateur_rpps_invalide(utilisateurs_enregistres):
    with pytest.raises(ValueError):
        app.register_utilisateur(
            nom="X", prenom="Y", courriel="x@y.fr",
            numero_rpps="12345",                    # 5 chiffres au lieu de 11
            mot_de_passe="Mdp_2024!",
        )


def test_register_utilisateur_confirmation_different(mocker):
    spied = mocker.patch("database.create_utilisateur")
    with pytest.raises(ValueError):
        app.register_utilisateur(
            nom="X", prenom="Y", courriel="x@y.fr",
            numero_rpps="10100317681",
            mot_de_passe="Mdp_2024!",
            mot_de_passe_confirmation="autre",
        )
    spied.assert_not_called()                       # rien insere


# ---------------------------------------------------------------
# authenticate : retrouvaille par hache courriel + bcrypt
# ---------------------------------------------------------------

def _table_lookup(utilisateurs_enregistres):
    """Reproduit le vrai get_utilisateur_by_courriel : cherche le hache du courriel."""
    table = utilisateurs_enregistres
    return lambda courriel: table.get(security.hash_email(courriel))


def test_authenticate_valide(mocker, utilisateurs_enregistres):
    app.register_utilisateur(
        nom="Martin", prenom="Bob", courriel="bob@example.fr",
        numero_rpps="10100317682", mot_de_passe="Bob-Mdp_2024",
    )
    # La base repond par le hache (comme get_utilisateur_by_courriel).
    mocker.patch(
        "database.get_utilisateur_by_courriel",
        side_effect=_table_lookup(utilisateurs_enregistres),
    )

    connecte = app.authenticate("Bob@Example.fr", "Bob-Mdp_2024")
    assert connecte["prenom"] == "Bob"


def test_authenticate_mauvais_mot_de_passe(mocker, utilisateurs_enregistres):
    app.register_utilisateur(
        nom="Martin", prenom="Bob", courriel="bob@example.fr",
        numero_rpps="10100317682", mot_de_passe="Bob-Mdp_2024",
    )
    mocker.patch(
        "database.get_utilisateur_by_courriel",
        side_effect=_table_lookup(utilisateurs_enregistres),
    )

    assert app.authenticate("bob@example.fr", "faux") is None


def test_authenticate_courriel_inconnu(mocker):
    mocker.patch("database.get_utilisateur_by_courriel", return_value=None)
    assert app.authenticate("personne@nulle.part", "x") is None
