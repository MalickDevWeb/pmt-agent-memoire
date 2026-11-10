# Diagrammes — École 221

> Responsable : Agent 11 (Modélisation) — mis à jour le 2026-11-07.
> Tous les diagrammes sont des fichiers texte PlantUML versionnés ; les images s'en déduisent (jamais dessinées à la main).

## Conventions de statut

| Statut | Signification |
|---|---|
| **Tel que construit** | Tiré du code ou de la configuration du dépôt (fichier:ligne cité en en-tête). |
| **Déduit** (pointillés) | Lien ou hébergement déduit d'un indice (nom, origine CORS…), sans fichier qui le prouve. |
| **Cible** (gris) | Fonctionnalité non implémentée, montrée pour mémoire uniquement. |

## Diagrammes manuels

### `contexte.puml` — Diagramme de contexte (Tel que construit)
Il montre École 221 face à ses cinq acteurs principaux (super-admin, directeur, enseignant, élève, parent), avec les routes API réservées à chaque rôle, et face aux services externes.
Seul Cloudinary est utilisé en conditions réelles (clés déclarées dans `render.yaml`) ; Brevo et Gemini/Mistral sont codés mais désactivés par défaut (`mock`). Le paiement mobile n'existe qu'en libellés écrits en dur, il est donc marqué **cible**.
Il sert au chapitre « analyse » du mémoire : délimiter le périmètre du système et ses dépendances externes.
Le directeur correspond au rôle `ADMIN` : c'est une correspondance supposée, car aucun rôle `DIRECTEUR` n'existe dans le code.

### `deploiement.puml` — Diagramme de déploiement (Tel que construit)
Il sépare les trois environnements réellement configurés : développement local (proxy Vite), Docker Compose (nginx, Spring Boot, PostgreSQL) et production sur Render (API, PostgreSQL 15, Redis).
L'hébergement du frontend sur Vercel est **déduit** de l'origine CORS autorisée : aucun fichier de configuration Vercel n'existe dans le dépôt.
Il sert au chapitre « architecture et mise en œuvre » et fait apparaître deux écarts : pas de Redis dans Docker Compose, et un schéma de base géré par `ddl-auto: update` sans migrations.

## Diagrammes générés (`generated/`)
`bd-*.puml` et `classes-*.puml` sont produits par `python3 audit/gen_diagrams.py` à partir des entités JPA. **Ne pas les modifier à la main.** Contrôle : `python3 audit/gen_diagrams.py --check` (36/36 à jour au 2026-11-07).
