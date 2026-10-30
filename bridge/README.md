# Bibliothèque CBZ locale (prototype)

Ce serveur Python est **un exemple autonome**, pas le pont complet de Manga Sama. Il sert les CBZ déjà présents sur le PC. Il n'intègre aucune source de récupération.

## Pré-requis

Python 3.11 ou plus récent. Aucun module externe.

Définir les variables d'environnement :
- `MANGASAMA_LIBRARY_DIR` : dossier contenant vos CBZ.
- `MANGASAMA_PAIRING_TOKEN` : jeton aléatoire d'au moins 32 caractères.
- `MANGASAMA_BIND` : par défaut `127.0.0.1`.
- `MANGASAMA_PORT` : par défaut `18879`.

Démarrer : `python bridge/local_library.py`

## Routes

Les requêtes utilisent l'en-tête `X-MangaSama-Pairing`.
- `GET /v1/health`
- `GET /v1/library`
- `GET /v1/files/<chemin-relatif>`

Le téléchargement transmet le SHA-256 dans `X-Content-SHA256`. Aucun chemin arbitraire en dehors de la bibliothèque ne doit être accessible.

## Sécurité et limites

**Ne pas ouvrir directement ce serveur HTTP sur Internet ou sur un LAN non fiable.** Par défaut il écoute uniquement sur l'ordinateur. Pour un appareil distant, il faudra un proxy HTTPS correctement authentifié et un appairage distinct. Les fichiers sont des CBZ locaux dont l'utilisateur possède le droit d'accès ; aucun fournisseur externe n'est intégré.

Le protocole final Kobo, l'import de fichiers, la découverte réseau, la protection contre les échanges de fichiers au cours d'un transfert et l'interface d'installation restent à développer et à tester. Ce prototype n'est pas un paquet installable sur Kobo.

Tests : `python -m unittest discover -s tests -v`.
