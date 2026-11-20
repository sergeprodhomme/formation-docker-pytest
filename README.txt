Bonne pratiques à garder en tête
--------------------------------
Image de base légère : privilégier python:3.x-slim pour des images plus petites et plus rapides à construire.
Gestion des dépendances : centraliser toutes mes dépendances de test (pytest, pytest-cov, pytest-xdist ...) dans un requirements.txt pour garantir la cohérence des versions.
Parallélisation : si ma suite devient longue, je peux installer python-xdist et lancer pytest -n auto à l'intérieur du conteneur pour paralléliser l'exécution.
