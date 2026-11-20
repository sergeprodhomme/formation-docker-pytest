"""Script de peuplement (seed) : insere des utilisateurs de demonstration.

Usage dans le conteneur web (DATABASE_URL pointe vers la BDD 'db') :
    docker compose run --rm web python seed.py
"""

import app


DEMO_USERS = [
    ("Dupont", "Alice", "alice@example.fr", "10100317681", "Alice-Mdp_2024"),
    ("Martin", "Bob", "bob@example.fr", "10100317682", "Bob-Mdp_2024"),
    ("Bernard", "Charlie", "charlie@example.fr", "10100317683", "Charlie-Mdp_2024"),
]


def main() -> None:
    for nom, prenom, courriel, rpps, mdp in DEMO_USERS:
        utilisateur = app.register_utilisateur(
            nom=nom, prenom=prenom, courriel=courriel,
            numero_rpps=rpps, mot_de_passe=mdp,
        )
        print(f" cree : id={utilisateur['id']} {prenom} {nom} <{courriel}>")


if __name__ == "__main__":
    main()
