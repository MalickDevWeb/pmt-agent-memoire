# Preuve de rendu — MOD-001 (Agent 11, Seynabou Cissé)

- Date : 2026-11-08, environ 19:21 (Dakar)
- Origine : écart n° 4 du rapport SUP-MOD-001 (docs/supervision/SUP-MOD-001.md)
- Emplacement : la preuve était attendue dans `docs/evidence/`, mais le moteur refuse l'écriture de l'Agent 11 dans ce dossier (hors périmètre). Elle est donc déposée ici, dans `docs/diagrams/`.

## Commandes exécutées (outil `executer` du pipeline)

| Commande | Équivalent | Sortie | Code |
|---|---|---|---|
| `diagrams-check` | `python3 audit/gen_diagrams.py --check` | `Bilan : 36/36 diagramme(s) à jour` | 0 |
| `diagrams-render` | `python3 audit/gen_diagrams.py --render` | aucune sortie texte | 0 |
| `git-status` | `git status --short` | aucun fichier de `docs/diagrams/` modifié ou non suivi au moment du contrôle | 0 |

## Faits constatés
- Après le rendu, `docs/diagrams/png/` contient `contexte.png` et `deploiement.png` (constat obtenu en listant le dossier).
- `docs/diagrams/.gitignore:1` contient `png/` : les PNG sont des **artefacts dérivés, non versionnés**. La source qui fait foi est le texte PlantUML versionné (`contexte.puml`, `deploiement.puml`), conformément à la règle 4 de la fiche 11. On reproduit les images avec `python3 audit/gen_diagrams.py --render`.

## Limites (non vérifié)
- La commande de rendu n'affiche rien. Je n'ai accès ni à la date de modification ni à la taille des PNG : je ne peux pas prouver qu'ils ont été réécrits par ce rendu.
- **Lisibilité non vérifiée** : je n'ai pas d'outil pour visualiser une image. Une vérification visuelle humaine est nécessaire (Tech Lead, ou Agent 09 lors de l'intégration au mémoire).
- Les 36 diagrammes générés (`generated/`) n'apparaissent pas sous forme de PNG dans `png/`.

## Point à trancher (proposition, pas décision)
Pour les images du mémoire, deux options :
- (a) versionner les PNG retenus ;
- (b) les garder non versionnés et les régénérer à l'export.

Ce choix revient au Tech Lead ou à l'Agent 02.
