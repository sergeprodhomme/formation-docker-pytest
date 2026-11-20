#!/usr/bin/sh
# Approche ideale pour les tests unitaires et pour verifier que la suite passe dans un environnement propre.
docker build -t my-pytest-app .
docker run --rm my-pytest-app
# docker run --rm my-pytest-app pytest --junitxml=report.xml
# (Pour des rapports plus riches.)

# Approche par docker-compose : pour tester avec des services
# si mes tests ont besoin de dépendances externes (BDD, cache, API), docker-compose orchestre mon conteneur de test et les services dont il depend.
# Utiliser le docker-compose.yml
docker compose run --rm web pytest -v
# La condition service_healthy garantit que la BDD est prete avant le lancement de tests, ce qui evite les echecs intermittents.