"""Trois facons de tester, de la plus simple a la plus utile avec pytest-mock."""

import database
import pytest

import app


# 1. Test unitaire pur : fonction sans dependance.
def test_add():
    assert app.add(2, 3) == 5


# 2. Parametrise : une seule fonction de test, plusieurs cas.
@pytest.mark.parametrize(
    "a, b, expected",
    [
        (2, 3, 5),
        (-1, 1, 0),
        (0.5, 0.25, 0.75),
    ],
)
def test_add_parametrized(a, b, expected):
    assert app.add(a, b) == expected


# 3. Mock : on isole app.fetch_user de database.get_user.
#    Le test ne depend plus du contenu de la fausse base :
#    il verifie QUE fetch_user transforme bien le resultat.
def test_fetch_user_formats_name(mocker):
    mocker.patch("database.get_user", return_value={"name": "charlie"})
    assert app.fetch_user(42) == "Charlie"


def test_fetch_user_returns_none_when_missing(mocker):
    mocker.patch("database.get_user", return_value=None)
    assert app.fetch_user(999) is None


# Bonus : la fonction reelle fonctionne aussi (base en memoire).
def test_fetch_user_against_fake_db():
    assert app.fetch_user(1) == "Alice"

# Ma premiere fonction de test avec pytest
def test_recuperer_utilisateur_Bob():
    assert app.fetch_user(2) == "Bob"