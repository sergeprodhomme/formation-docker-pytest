"""Ajouter un utilisateur a la base dans le volume Docker.

Usage :
    docker compose run --rm web python ajout_utilisateur.py \
        --nom "Durand" --prenom "Eve" \
        --courriel "eve@exemple.fr" \
        --rpps 10100317684 \
        --mdp "Eve-Mdp_2024"

Le mot de passe est hache en bcrypt, le courriel en HMAC, AVANT l'insertion :
la base ne voit jamais les valeurs en clair.

Persistance : l'ecriture va dans le volume pgdata — elle survit a
'docker compose down'. Elle n'est perdue qu'avec 'down -v' (efface le volume),
auquel cas le schema est rejoue et 'python seed.py' remet les comptes de demo.
"""

import argparse
import sys

import app


def main() -> int:
    parseur = argparse.ArgumentParser(description="Creer un utilisateur dans la base de test.")
    parseur.add_argument("--nom", required=True)
    parseur.add_argument("--prenom", required=True)
    parseur.add_argument("--courriel", required=True)
    parseur.add_argument("--rpps", required=True, help="11 chiffres")
    parseur.add_argument("--mdp", required=True, help="mot de passe en clair, hache avant insertion")
    args = parseur.parse_args()

    try:
        utilisateur = app.register_utilisateur(
            nom=args.nom, prenom=args.prenom, courriel=args.courriel,
            numero_rpps=args.rpps, mot_de_passe=args.mdp,
            mot_de_passe_confirmation=args.mdp,
        )
    except ValueError as err:
        # Validation refusée (RPPS, confirmation) : message pour l'humain.
        print(f"Refuse : {err}")
        return 1
    except Exception as err:
        # Violation d'unicite (courriel/RPPS deja pris) ou souci base.
        print(f"Erreur : {err}")
        return 1

    print(f"OK : id={utilisateur['id']} {utilisateur['prenom']} {utilisateur['nom']}"
          f" <{utilisateur['courriel']}> rpps={utilisateur['numero_rpps']}")
    print(f"     courriel_hash={utilisateur['courriel_hash'][:16]}…")
    print(f"     mot_de_passe_hash={utilisateur['mot_de_passe_hash'][:20]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
