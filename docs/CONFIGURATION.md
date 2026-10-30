# Pont PC

La Kobo communique avec un serveur PC appaire. L'adresse est configurable et aucun fournisseur de contenu n'est inscrit dans l'application publique.

Le protocole doit prendre en charge catalogue, recherche, fiche, preparation, suivi des lots, annulation, historique et transfert CBZ.

Le CBZ est transfere vers un fichier temporaire puis controle par SHA-256 avant import. Le mode Dropbox reste optionnel. Aucun fichier existant ne doit etre ecrase.

Les bases, jetons, caches, historiques et connecteurs de recuperation restent hors du depot. Les connecteurs publies devront respecter les droits sur les sources et les contenus.
