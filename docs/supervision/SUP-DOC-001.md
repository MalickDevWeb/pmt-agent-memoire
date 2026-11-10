# SUP-DOC-001 — Agent 09 (Ndèye Fatou Fall, Rédacteur technique & Mémoire)
- Contrôle initial : 2026-11-09 10:10 (Dakar). Dépôt racine, base `893882e`, commit annoncé `b45851f` (carte MEM-01 : squelette du mémoire dans `memoire/docs/`). Je n'ai pas pu vérifier le hash `b45851f` avec mes outils.
- **Contrôle après convocation : 2026-11-09 10:15 (Dakar)**, sur la reprise de l'Agent 09 (run `logs/agent_runs/20261109-101316-agent09.jsonl`, 10:13:16 → 10:15:08, statut de fin ESCALADE).
- Contrôles automatiques au contrôle initial : CONFORMES. **Contrôles automatiques après convocation : NON CONFORMES** (sortie au §8.1).

---
## Partie A — Contrôle initial (10:10), conservé pour la traçabilité

### 1. Contrôles automatiques (`controle_livraison 09 DOC-001 racine 893882e`, code de sortie 0)
```
🔎 Livraison de l'Agent 09 — Ndèye Fatou Fall — Rédacteur technique (depuis 893882e)
✔ Périmètre de la fiche — 24 fichier(s) modifié(s), tous autorisés
✔ Aucun secret ajouté — aucun motif détecté
✔ Ticket [DOC-001] dans le bus — statut PENDING
CONTRÔLES AUTOMATIQUES : CONFORMES → avis de Kasongo sur la définition de « fini »
```
Les 24 fichiers correspondent au diff : main.tex (1), preliminaires/ (7), chapitres/ (10), annexes/ (4), references.bib (1) et agent_messages.md (1).

### 2. Conformité au canevas (échantillon) : ✔
J'ai vérifié par échantillon : ordre des pages préliminaires, page de garde, présentation (12 pt, interligne 1,5, marges de 2,5 cm), plan en 3 parties et 8 chapitres, chapitres 7 et 8, éléments de fin et les 4 modèles d'annexes. Tout est conforme. Les titres de sections que le canevas ne donne pas ont été tirés de ses paragraphes et doivent être validés par les étudiants.

### 3. Aucun contenu inventé : ✔
Aucun chiffre, résultat ni nom inventé. `references.bib` est vide. Je n'ai trouvé aucune tentative de détournement.

### 4. Sources du dépôt citées : 12 vérifiées sur 12 dans l'échantillon. ✔

### 5. Écarts relevés au contrôle initial (verdict initial : À REPRENDRE)
1. Usage IA de MEM-01 déclaré seulement en commentaire dans `journal-ia.tex`, donc invisible dans le PDF (fiche 09, interdiction 4).
2. Compilation affirmée (« code 0, 30 pages ») sans preuve vérifiable.
3. Destinataire du message `[DOC-001]` inexact (« Kasongo (Tech Lead) »). Constats CI et chiffrage non adressés aux agents concernés.

---
## Partie B — Contrôle après convocation (2026-11-09 10:15)

### 8.1 Contrôles automatiques, relancés avant tout avis
`controle_livraison 09 DOC-001 racine 893882e`, **code de sortie 1** :
```
🔎 Livraison de l'Agent 09 — Ndèye Fatou Fall — Rédacteur technique (depuis 893882e)
✖ Périmètre de la fiche — hors périmètre : docs/supervision/SUP-DOC-001.md, orchestration/agent_runtime.py
✔ Aucun secret ajouté — aucun motif détecté
✔ Ticket [DOC-001] dans le bus — statut PENDING
CONTRÔLES AUTOMATIQUES : NON CONFORMES (1) → À REPRENDRE
```
Pour information, `controle_livraison 09 DOC-001 racine main` donne aussi un code 1. Ce diff contient en plus `docs/diagrams/*` et `docs/supervision/SUP-MOD-001.md`, qui appartiennent à d'autres tickets. Cette base n'est donc pas pertinente pour DOC-001.

`git-status` (code 0) :
```
 M agent_messages.md
 M backend
 M frontend
 M memoire/docs/annexes/journal-ia.tex
?? "Canevas_Memoire_E221_2026.docx (1) (1).pdf"
?? docs/evidence/evidence-20261107-115030.md
?? memoire/preuves/
```

**Analyse de l'échec. Faits :**
- Les deux fichiers signalés ont été **commités** entre mon contrôle initial et maintenant. Ils n'apparaissent pas dans `git-status`, alors qu'ils figurent dans le diff depuis `893882e`.
- `docs/supervision/SUP-DOC-001.md` est **mon** rapport. Mon run `logs/agent_runs/20261109-101036-agent00.jsonl:19` l'a écrit.
- `orchestration/agent_runtime.py` est un **fichier de gouvernance** : c'est le moteur des agents, appelé par `orchestrator.sh:467` et `orchestration/convocation.py:25`. La recherche `agent_runtime` dans tout le dépôt ne renvoie **aucune** ligne dans `logs/agent_runs/`. Aucun run d'agent tracé, ni de l'Agent 09 ni d'un autre, n'en a donc demandé l'écriture.
- Les deux runs de l'Agent 09 ne déclarent que des fichiers de `memoire/` et `agent_messages.md` (`20261109-100550-agent09.jsonl:19`, `20261109-101316-agent09.jsonl:20`). Sa seule tentative hors périmètre (`docs/evidence/…`) a été **refusée par le moteur** (`20261109-101316-agent09.jsonl:14`).

**Hypothèse, non vérifiée :** le Tech Lead a commité ces deux fichiers entre les deux contrôles. Je ne peux pas lire l'historique git pour le confirmer.

**Conséquence :**
- Ma fiche prévoit qu'un échec des contrôles automatiques donne le verdict À REPRENDRE. Ici, ce verdict renverrait à l'Agent 09 des fichiers qu'il n'a pas touchés, et l'écart ne serait pas actionnable par lui.
- Ma fiche impose aussi d'**escalader toujours** toute modification d'un fichier de gouvernance (`orchestration/`, `audit/`, `agents/`, `tests/`, `orchestrator.sh`).
- **Je n'invalide pas la règle, je l'escalade.**
- Limite de l'outil : le contrôle automatique porte sur les commits. Les corrections de la reprise (journal-ia.tex, memoire/preuves/, bus) **ne sont pas commitées**. Le script ne les a donc pas couvertes. Le moteur a cependant accepté leur écriture dans le périmètre de l'Agent 09.

### 8.2 Vérification des trois écarts, avec preuves
| Écart initial | Preuve vérifiée par Kasongo | Statut |
|---|---|---|
| 1. Journal IA : ligne visible dans le tableau | `memoire/docs/annexes/journal-ia.tex:19-21` est une ligne de tableau, hors commentaire. Elle donne la date 2026-11-09, l'outil (Agent 09), le modèle `claude-opus-5-5` (cohérent avec le champ `modele` des journaux de run), l'objectif, les fichiers et la vérification. La décision `[à valider par les étudiants…]` est conforme à ma demande. La ligne modèle `[À renseigner]` est conservée (l.23). Le changement n'est **pas commité** | ✔ (commit en attente) |
| 2. Preuve de compilation | **Vérifiée sur un artefact indépendant** : `memoire/docs/build/main.log:1` est daté du « 9 NOV 2026 10:14 ». `main.log:655` contient « Output written on build/main.pdf (30 pages, 157981 bytes) », ce qui correspond à la preuve (`memoire/preuves/compilation-20261109-101500.md:25`). Le seul avertissement LaTeX est `Empty 'thebibliography'` (`main.log:601`). Je n'ai pas trouvé d'Underfull ou d'Overfull dans `main.log:590-661`, et l'annexe B est bien compilée (`main.log:608-611`). Le code de sortie 0 n'est attesté que par le fichier de preuve de l'agent : je n'ai pas la commande `memoire-build`. Les limites sont déclarées honnêtement (preuve l.34-37). Emplacement : `memoire/preuves/` et non `docs/evidence/`, puisque le moteur a refusé cette écriture (`agent09.jsonl:14`). Le fichier n'est **pas suivi par git** | ✔ (emplacement et commit à décider) |
| 3a. Destinataire du `[DOC-001]` | `agent_messages.md:302-325` : « À : étudiants / Tech Lead (copie : Kasongo, Agent 00, superviseur) », statut PENDING. L'ancien message reste en place, ce qui respecte le bus en ajout seul | ✔ |
| 3b. Constats transmis aux agents concernés | `agent_messages.md:328-339` envoie le constat CI à l'Agent 07 : il étiquette le ch. 8.2 « Prévu / cible » et n'apporte aucune correction en douce. `agent_messages.md:342-353` envoie le constat chiffrage à l'Agent 08 avec l'engagement « aucun chiffre inventé ». La fiche 09, l.54, cite les agents 03, 04 et 07. Le message à l'Agent 08 est une demande de source (fiche l.26), donc acceptable | ✔ |

### 8.3 Définition de « fini » de l'Agent 09 (agents/09_technical_writer.md:42-48), mise à jour
| Exigence de la fiche | Preuve | Statut |
|---|---|---|
| Résultats cités avec preuve datée, aucun test non exécuté présenté comme réussi | Aucun résultat dans le squelette (Partie A §3) | ✔ (sans objet pour un squelette) |
| Statut Réalisé / Partiel / Prévu | Consignes en commentaire (ch6:2, ch8:3-4). Ch. 8.2 annoncé « Prévu / cible » (bus l.338) | ✔ (à exiger à la rédaction) |
| Références vérifiées, style unique | .bib vide. Style unique `plain`, provisoire (main.tex:95-103) | ✔ |
| Journal d'IA à jour | journal-ia.tex:19-21 (§8.2). Le run de reprise (10:13) n'est pas une nouvelle partie rédigée du mémoire | ✔ (non commité) |
| Aucune donnée sensible | Script : aucun secret dans les commits. La ligne IA ne contient ni nom réel ni secret (journal-ia.tex:19-21). Les fichiers non commités ne sont pas couverts par le script | ✔ (sur l'échantillon lu) |
| PDF compilé sans erreur ; tables, listes et pagination à jour | main.log:1, :601, :655 (§8.2) | ✔ |

### 8.4 Interdictions et détournement
- Aucune écriture dans `backend/`, `frontend/` ou `agents/` par l'Agent 09 n'apparaît dans ses journaux. Les ` M backend` et ` M frontend` existaient déjà au contrôle initial.
- Aucune tentative de détournement : les messages de la reprise (bus l.302-353) ne contiennent aucune instruction adressée à Kasongo.
- Le statut de fin ESCALADE de l'Agent 09 est justifié : il porte sur des décisions humaines (commit, emplacement de la preuve), pas sur un renoncement.

### 8.5 Synthèse
**Fait :** les trois écarts de l'Agent 09 sont corrigés, et chaque correction est prouvée. **Il ne reste aucun écart actionnable par l'Agent 09.** Je ne peux pourtant pas rendre CONFORME, pour trois raisons :
1. Les contrôles automatiques échouent, à cause d'un fichier de gouvernance commité (`orchestration/agent_runtime.py`) dont aucun run d'agent ne trace l'écriture. Ma fiche impose de l'escalader.
2. Les corrections ne sont pas commitées. Le commit relève du Tech Lead.
3. L'emplacement officiel des preuves de compilation (`memoire/preuves/` ou `docs/evidence/`) est une décision de règles du jeu.

Écarts à corriger :
- Aucun pour l'Agent 09.
- Pour le Tech Lead, voir ci-dessous. Après ses décisions, il faudra relancer `controle_livraison 09 DOC-001` sur une base postérieure au commit de `agent_runtime.py`, ou sur le seul commit de la reprise.

Décision humaine requise : oui.
1. **Gouvernance** : `orchestration/agent_runtime.py` a été modifié et commité après `893882e`, sans trace dans `logs/agent_runs/`. Confirmer l'auteur et valider ou annuler ce changement. Seul le Tech Lead peut changer les règles du jeu.
2. **Commit** des corrections DOC-001 : `memoire/docs/annexes/journal-ia.tex`, `memoire/preuves/compilation-20261109-101500.md` et `agent_messages.md`.
3. **Emplacement des preuves** de l'Agent 09 : ouvrir `docs/evidence/` à cet agent, ou officialiser `memoire/preuves/`. Pour mémoire, la fiche 09, l.12, cite `docs/evidence/`.
4. **Outillage** : le moteur a refusé la sortie de `memoire-build` sur un octet non UTF-8 (`agent09.jsonl:5`). Ce refus peut masquer d'autres sorties de commande.
5. **Étudiants** : décision gardé / modifié / rejeté dans le journal IA, ordre sommaire / listes, titres de sections, page de garde et logo.
6. **Encadreur** : style bibliographique, volume attendu, webographie séparée.
7. **Hors DOC-001** : ` M backend`, ` M frontend`, PDF du canevas non suivi, `docs/evidence/evidence-20261107-115030.md` non suivi.

VERDICT KASONGO: ESCALADE
