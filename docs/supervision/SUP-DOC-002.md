# SUP-DOC-002 — Agent 09 (Ndèye Fatou Fall, rédactrice technique)
- Date : 2026-11-09 11:01 (Dakar). Commit contrôlé : bfb126b (base b823340), dépôt racine.
- Livrable : introduction générale (MEM-04, `memoire/docs/chapitres/introduction.tex`) et §8.5 (MEM-18, `ch8-deploiement.tex:38-178`), avec la ligne DOC-002 de `annexes/journal-ia.tex`.
- Contrôles automatiques : CONFORMES

```
controle_livraison 09 DOC-002 racine b823340 — code de sortie 0
✔ Périmètre de la fiche — 5 fichier(s) modifié(s), tous autorisés
✔ Aucun secret ajouté — aucun motif détecté
✔ Ticket [DOC-002] dans le bus — statut PENDING
CONTRÔLES AUTOMATIQUES : CONFORMES
```
Limite : le script ne sait pas qui a écrit quoi. `memoire/docs/style-e221.sty` est compté dans le périmètre de l'Agent 09 (`audit/check_handover.py:43`, `memoire/*`), alors que, d'après le Tech Lead, il l'a modifié lui-même dans ce même commit. Je n'ai pas d'outil pour lire `git log` ou le diff : je ne peux donc pas répartir les 5 fichiers entre l'agent et le Tech Lead.

## 1. Échantillon de vérification des sources (22 affirmations, 21 exactes)
| # | Affirmation (emplacement) | Source vérifiée | Statut |
|---|---|---|---|
| 1 | Tableau des runs : 10 durées et 10 coûts (ch8:146-155) | Recalcul depuis les lignes debut et fin des 10 journaux (`logs/agent_runs/*.jsonl`, de 20261108-185219 à 20261109-101509). Par exemple 0,54044 → 0,540 et 43 s, 0,99076 → 0,991 et 4 min 14. Les 10 lignes concordent | ✔ |
| 2 | Totaux 20 min 27 et 4,911 $ (ch8:157) | 1 227 s = 20 min 27 ; somme 4,91121 $ | ✔ |
| 3 | Répartition : 3 TERMINE, 2 PARTIEL, 4 ESCALADE, 1 BUDGET_ATTEINT ; Kasongo 2,685 $, Agent 09 1,495 $, Agent 11 0,732 $ (ch8:165) | Recalcul : 2,68487 $, 1,49484 $ et 0,7315 $. Avec les arrondis, la somme des trois donne 4,912 $ et non 4,911 $ | ✔ (écart d'arrondi, voir écart 3) |
| 4 | Budget 0,50 $ dépassé à 0,540 $ (ch8:169) | `20261108-185219-agent00.jsonl:1` (budget 0.5) et `:10` | ✔ |
| 5 | Budget vérifié avant chaque tour (ch8:169) | `agent_runtime.py:313-315` | ✔ |
| 6 | Refus d'écriture dans docs/evidence et défaut d'encodage UTF-8 (ch8:170-171) | `20261108-192042-agent11.jsonl:6`, `20261109-101316-agent09.jsonl:14` et `:5` | ✔ |
| 7 | Convocations MOD-001 et DOC-001 : escalade dès la 1re tentative (ch8:86) | `convocations.json:2-21` | ✔ |
| 8 | Mécanisme de convocation, max 2 tentatives (ch8:86) | `convocation.py:7-14`, `equipe.json:20-26` | ✔ |
| 9 | Modèle `claude-opus-5-5` et barème des prix (ch8:84, 165) | `agent_runtime.py:28`, `:29-31`, `:207-211` | ✔ |
| 10 | Liste blanche de commandes, sans push ni déploiement (ch8:117) | `agent_runtime.py:36-58` | ✔ |
| 11 | Périmètre, secrets et bus en ajout seul (ch8:115-116, 121) | `agent_runtime.py:154-157`, `:115-124`, `:160-161`, `:173-185` | ✔ |
| 12 | Rien n'est commité automatiquement (ch8:121) | `agent_runtime.py:375`, `convocation.py:13` | ✔ |
| 13 | Journalisation : taille du contenu et refus tracés (ch8:131) | `agent_runtime.py:333-337`, `:355-357` | ✔ |
| 14 | Horaires (Dakar) et dérogation (ch8:119) | `agent_runtime.py:221-229`, `:258-268`, `:308-309` ; `equipe.json:3` | ✔ |
| 15 | Aucune mémoire d'un run à l'autre (ch8:84) | `agent_runtime.py:288-292` | ✔ |
| 16 | Tableau des agents et des périmètres (ch8:63-74) | `check_handover.py:28-53`, `equipe.json:6-19` | ✔ (simplifié : `backend/render.yaml`, autorisé pour l'Agent 10 et interdit à l'Agent 03, n'est pas mentionné) |
| 17 | Verdicts ESCALADE des trois tickets (ch8:123) | `SUP-SEC-003.md:47`, `SUP-MOD-001.md:114`, `SUP-DOC-001.md:113` | ✔ |
| 18 | Écarts relevés par Kasongo sur SEC-003, MOD-001 et DOC-001 (ch8:125, 172) | `SUP-SEC-003.md:22-27`, `:35`, `:36` ; `SUP-MOD-001.md:78-86` ; `SUP-DOC-001.md:27-30`, `:96` | ✔ |
| 19 | « Les **trois** rapports indiquent qu'aucune tentative de détournement n'a été détectée » (ch8:129) | La note ne cite que MOD-001:54 et DOC-001:23 et 91. La recherche « détournement » dans `docs/supervision/` ne trouve **rien** dans SUP-SEC-003 | ✖ inexact |
| 20 | BR-01 classée CRITIQUE, BR-03 à BR-05 (intro:18, 35) | `docs/requirements.md:96-100` | ✔ |
| 21 | Hors périmètre : cryptomonnaie et reconnaissance faciale (intro:42) | `docs/requirements.md:38-39` | ✔ |
| 22 | Spring Boot 3 hexagonal et React 18 (intro:42) | `docs/architecture.md:13`, `:20` | ✔ |

Autres sources contrôlées : `agents/00_supervisor.md`, lignes 5-9, 9, 18, 28 et 32-37 (✔) ; `orchestrator.sh:464-468` (✔). « Six outils au plus » (ch8:84) : l'outil `terminer` n'est pas compté (`agent_runtime.py:85-106`), ce qui est une imprécision mineure.

## 2. Statuts Réalisé / Partiel / Prévu
- CI/CD marquée **Prévu** : aucun workflow n'existe. Le journal du run de l'agent le confirme (`20261109-105529-agent09.jsonl:24-25`, pas de `.github/` dans backend ni frontend). ✔
- Remplaçant marqué **Prévu** : il n'a jamais été exécuté (`convocations.json`). ✔
- Validation humaine marquée **Partiel** : aucune décision du Tech Lead n'est consignée dans le bus. ✔
- Test de détournement marqué **Prévu** : statut juste, mais il s'appuie sur l'affirmation n° 19, qui est inexacte.
- Statut global du §8.5 : « partiellement réalisé », ce qui est cohérent.

## 3. Définition de « fini » (agents/09_technical_writer.md:43-48)
| Exigence | Preuve | Statut |
|---|---|---|
| Résultats avec preuve datée, aucun test fictif | §1 : 21 affirmations sur 22 sont exactes, l'affirmation n° 19 est inexacte | ✖ (1 écart) |
| Statut Réalisé / Partiel / Prévu | §2 | ✔ |
| Références vérifiées, style unique | Aucune référence bibliographique ajoutée, uniquement des notes vers le dépôt | ✔ (sans objet) |
| Journal d'IA à jour | `journal-ia.tex:8`, `:25` (ligne DOC-002) | ✔ |
| Aucune donnée sensible | Script : aucun secret. Les secrets du §8.5.3 sont cités sans être recopiés (ch8:131) | ✔ |
| Le PDF compile sans erreur | `memoire-build` exécuté par Kasongo : code 0, « All targets (build/main.pdf) are up-to-date ». `build/main.log:1` est daté du 9 NOV 2026 11:01 et `main.toc:10`, `:63-78` contient l'introduction et le §8.5. La recherche d'erreurs dans `main.log` a échoué (fichier non UTF-8) : l'absence d'avertissements n'est pas vérifiée. La compilation réussie vient du correctif du Tech Lead, pas de l'agent, qui a déclaré honnêtement son échec (bus l.402) | ✔ (avec réserves) |

## 4. Interdictions et passage de témoin
- L'agent n'a modifié ni `backend/`, ni `frontend/`, ni `agents/` d'après le script.
- `main.tex` : l'agent a ajouté `\usetikzlibrary{babel}`, qu'il juge lui-même « sans effet » (bus l.400). Il reste à décider s'il faut garder ou retirer cet ajout.
- Message `[DOC-002]` (bus l.387-406) : format correct, statut PENDING, copie aux étudiants et au Tech Lead, points à relire et question pour l'encadreur (intitulé de la partie 1 comparé au canevas l.86). ✔
- Aucune tentative de détournement trouvée dans le bus ni dans les livrables lus.
- **Conflit d'intérêts à signaler** : le §8.5 décrit et évalue les contrôles de Kasongo (ch8:82, 123, 129, 172). J'ai vérifié les sources, mais je ne suis pas neutre sur ce contenu. Une relecture humaine est nécessaire.

VERDICT KASONGO: ESCALADE
Écarts à corriger (Agent 09, après décision du Tech Lead) :
1. ch8:129 : remplacer « Les trois rapports » par « Les rapports SUP-MOD-001 et SUP-DOC-001 », ou citer une ligne de SUP-SEC-003 qui le dise (aucune n'existe à ce jour).
2. ch8:84 : signaler l'outil `terminer` (sept outils au plus), ou reformuler.
3. ch8:165 : préciser que les sous-totaux sont arrondis (leur somme donne 4,912 $ et non 4,911 $).
4. Facultatif : ch8:66 et :73, mentionner `render.yaml` (interdit à l'Agent 03, autorisé pour l'Agent 10).
Décision humaine requise : oui.
1. Commit bfb126b : il mélange la livraison de l'agent et le correctif du Tech Lead (`style-e221.sty`). Le script attribue ce fichier à l'Agent 09. Il faut confirmer par écrit (bus ou message de commit) quels fichiers viennent du Tech Lead, pour garder la traçabilité.
2. `main.tex` : garder ou retirer `\usetikzlibrary{babel}`.
3. Le §8.5 évalue le superviseur : prévoir une relecture humaine ou par un tiers, pas par Kasongo seul.
4. Outillage : `main.log` n'est pas consultable par recherche (encodage), ce qui fait le même défaut que pour DOC-001.
5. Étudiants : problématique, repères [À COMPLÉTER] et intitulé de la partie 1.
