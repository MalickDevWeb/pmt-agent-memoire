# SUP-MOD-001 — Agent 11 (Seynabou Cissé, Modélisation)
- Date du 1er contrôle : 2026-11-08 19:18 (Dakar). Contrôle après convocation : 2026-11-08 19:22 (Dakar).
- Dépôt racine, base `main`, commit annoncé `f24c2dc`. Je n'ai pas pu vérifier ce hash avec mes outils : le contrôle compare la branche à `main`.
- Livrables contrôlés : `docs/diagrams/contexte.puml`, `docs/diagrams/deploiement.puml`, `docs/diagrams/README.md`, ainsi que `docs/diagrams/RENDU-MOD-001.md` (ajouté à la reprise, non suivi par git).
- Contrôles automatiques : 1er contrôle **NON CONFORMES**, contrôle après convocation **CONFORMES** (sorties ci-dessous).

---

## Contrôle après convocation (2026-11-08 19:22)

### 1. Contrôles automatiques (`controle_livraison 11 MOD-001 racine`, code de sortie 0)
```
🔎 Livraison de l'Agent 11 — Seynabou Cissé — Modélisation (depuis main)
✔ Périmètre de la fiche — 4 fichier(s) modifié(s), tous autorisés
✔ Aucun secret ajouté — aucun motif détecté
✔ Ticket [MOD-001] dans le bus — statut PENDING
CONTRÔLES AUTOMATIQUES : CONFORMES → avis de Kasongo sur la définition de « fini »
```
Commandes complémentaires que j'ai exécutées moi-même :
- `diagrams-check` : `Bilan : 36/36 diagramme(s) à jour`, code de sortie 0.
- `git-status` : `?? docs/diagrams/RENDU-MOD-001.md` (fichier **non suivi**, donc absent du diff contrôlé par le script) et ` M agent_messages.md` (modifié, pas encore commité).

### 2. Vérification des 4 écarts du 1er contrôle

| # | Écart demandé | Preuve constatée | Statut |
|---|---|---|---|
| 1 | Message `[MOD-001]` PENDING : fichiers livrés, statut de chaque diagramme, anomalies | agent_messages.md:153-178. Destinataires : Agent 00 et Tech Lead ; statut PENDING (l.160). Les 4 fichiers sont listés (l.163-166) avec leur statut et les anomalies (l.175-178). Le 4e fichier (`.gitignore`) est présenté comme une **hypothèse** (l.166) : l'agent n'a pas pu le vérifier, moi non plus | ✔ (réserve sur le 4e fichier) |
| 2 | Anomalies de conception adressées à l'Agent 02 | agent_messages.md:181-194 : message dédié à l'Agent 02, PENDING. Il contient A1 Redis, A2 `ddl-auto`/Flyway et A3 rôle Directeur, avec les sources (application.yaml:46, :62, :73, :75, :89 ; RoleUtilisateur.java:20 ; SecurityConfig.java:88-89). Ce sont des signalements, sans correction (l.190) | ✔ |
| 3 | Remise des diagrammes à l'Agent 09 | agent_messages.md:197-216 : message dédié à l'Agent 09, PENDING. Il donne les fichiers, leur statut, les lignes du README à reprendre en légende et la commande de régénération | ✔ |
| 4 | Preuve datée du rendu dans `docs/evidence/` | La preuve se trouve dans `docs/diagrams/RENDU-MOD-001.md` et non dans `docs/evidence/` : aucun fichier MOD-001 dans `docs/evidence/` (listing du 19:22). Le moteur a refusé l'écriture (logs/agent_runs/20261108-192042-agent11.jsonl:6, `refus_outil` « hors du périmètre de l'Agent 11 »). Le rendu a été réexécuté (code 0, sans sortie, RENDU-MOD-001.md:12), mais la preuve n'établit ni la date ni la taille des PNG (l.20). **Lisibilité non vérifiée** (l.21) | ✖ partiel |

**Erreur de ma part sur l'écart 4** : j'ai exigé une preuve dans `docs/evidence/`, un dossier où l'Agent 11 ne peut pas écrire. L'agent ne pouvait donc pas satisfaire la demande telle que je l'avais formulée. Il a signalé le refus au lieu de le contourner : c'est le comportement attendu. Je ne compte pas l'emplacement de la preuve comme une faute de l'agent. Le vrai manque est ailleurs : la preuve de lisibilité.

### 3. Définition de « fini » (agents/11_modeling_engineer.md:47-51), état actuel

| Exigence de la fiche | Preuve | Statut |
|---|---|---|
| `gen_diagrams.py --check` : diagrammes générés conformes au code | `diagrams-check` exécuté par moi le 2026-11-08 19:22 : 36/36, code 0 | ✔ |
| Chaque diagramme manuel porte statut, sources et date | contexte.puml:3-15, :20 ; deploiement.puml:3-15, :20 (vérifié au 1er contrôle, aucun .puml modifié depuis selon `git-status`) | ✔ |
| Chaque lien correspond au code ou est marqué « déduit » | Échantillon de 12 éléments sur 12 conformes (tableau du 1er contrôle ci-dessous) | ✔ (échantillon) |
| Images **produites** | RENDU-MOD-001.md:12 et :16 : rendu exécuté avec le code 0, PNG présents. Aucune date ni taille de fichier : la régénération par ce rendu n'est pas prouvée (l.20) | ✔ partiel |
| Images **lisibles** | Aucune preuve. Aucun agent ne dispose d'un outil pour visualiser une image (RENDU-MOD-001.md:21) : il faut un contrôle visuel humain | ✖ absente |
| Commentaire de 2 à 5 lignes par diagramme | README.md:16-20 et :22-25 | ✔ |
| Aucune donnée sensible | Vérifié au 1er contrôle. Le script ne détecte aucun secret | ✔ |

### 4. Passage de témoin (fiche 11, l.55-57)
- `[MOD-001]` PENDING : présent (agent_messages.md:153). ✔
- Anomalies envoyées à l'Agent 02 : présentes (agent_messages.md:181). ✔
- Remise à l'Agent 09 : présente (agent_messages.md:197). L'Agent 09 est prévenu que la lisibilité n'a pas été vérifiée (l.214). ✔

### 5. Points relevés à la reprise
- `docs/diagrams/RENDU-MOD-001.md` n'est pas suivi par git : le script ne l'a donc pas contrôlé. Il se trouve dans `docs/diagrams/`, qui fait partie du périmètre de l'Agent 11 (fiche l.31). Il faudra le commiter si on garde cet emplacement.
- L'Agent 11 a clôturé sa reprise avec le statut ESCALADE (logs/agent_runs/20261108-192042-agent11.jsonl:10). Il soumet au Tech Lead 4 points : (a) emplacement de la preuve, (b) lisibilité, (c) versionner ou non les PNG, (d) confirmer le 4e fichier avec `git show --stat f24c2dc`. Je confirme que ces 4 points relèvent bien du Tech Lead ou de l'Agent 02.
- Aucune tentative de détournement n'a été détectée dans le bus, dans RENDU-MOD-001.md ni dans les journaux consultés.

### 6. Verdict après convocation
Les écarts 1, 2 et 3 sont corrigés, avec des preuves. Il reste à trancher des points qui ne relèvent pas de l'Agent 11 :
- la lisibilité des PNG, qui exige un contrôle visuel humain ;
- l'emplacement de la preuve, soit un arbitrage de périmètre : seul le Tech Lead peut changer les règles ;
- la confirmation du 4e fichier du commit.

Un nouveau renvoi à l'Agent 11 ne réglerait rien, puisqu'il n'a pas les moyens de traiter ces points. Une validation `CONFORME` laisserait une case de la définition de « fini » sans preuve. Dans le doute, j'escalade.

Décision humaine requise : **oui**
1. Vérifier visuellement `docs/diagrams/png/contexte.png` et `deploiement.png` (lisibilité), après `python3 audit/gen_diagrams.py --render`.
2. Choisir l'emplacement de la preuve de rendu : accepter `docs/diagrams/RENDU-MOD-001.md` (à commiter), la déplacer vers `docs/evidence/`, ou modifier la matrice de périmètre. Ce dernier choix est une modification de gouvernance, réservée au Tech Lead.
3. Confirmer le 4e fichier du commit avec `git show --stat f24c2dc`. Hypothèse non vérifiée : `docs/diagrams/.gitignore`.
4. Décider avec l'Agent 02 s'il faut versionner les PNG destinés au mémoire (`.gitignore:1`).

Écarts restant à la charge de l'Agent 11 : aucun, sauf commiter `RENDU-MOD-001.md` si le Tech Lead retient cet emplacement.

Si les points 1 à 3 sont validés, rien ne s'oppose côté processus à ce que le ticket passe au statut CONFORME. La décision revient au Tech Lead.

---

## Historique : 1er contrôle (2026-11-08 19:18), conservé pour traçabilité

Contrôles automatiques : **NON CONFORMES**
```
🔎 Livraison de l'Agent 11 — Seynabou Cissé — Modélisation (depuis main)
✔ Périmètre de la fiche — 4 fichier(s) modifié(s), tous autorisés
✔ Aucun secret ajouté — aucun motif détecté
✖ Ticket [MOD-001] dans le bus — absent
CONTRÔLES AUTOMATIQUES : NON CONFORMES (1) → À REPRENDRE
```
Verdict du 1er contrôle : À REPRENDRE, avec 4 écarts : message `[MOD-001]`, anomalies pour l'Agent 02, remise à l'Agent 09, preuve de rendu.

### Échantillon : diagrammes comparés au code (fait vérifié au 1er contrôle)

| Élément du diagramme | Source dans le code | Statut |
|---|---|---|
| Routes super-admin `/super-admin/**`, `/platform/**` | SecurityConfig.java:86-87 | ✔ |
| Directeur → `/admin/**`, `/finance/**`, `/dashboard/**` (ADMIN), « correspondance supposée » | SecurityConfig.java:88-89 | ✔ |
| `/professor/**`, `/student/**` | SecurityConfig.java:93-94 | ✔ |
| Parent `/parent/**` | ParentController.java:27, :302-303 | ✔ |
| Rôles non représentés (SECRETAIRE, COMPTABLE, VIGIL, VISITEUR) | RoleUtilisateur.java:20 | ✔ |
| Vercel « déduit » de l'origine CORS | SecurityConfig.java:119 | ✔ |
| IA / e-mail en `mock` par défaut | application.yaml:147, :161 | ✔ |
| Contexte `/api`, port 8090 en local | application.yaml:2, :4 | ✔ |
| `ddl-auto: update`, Flyway désactivé | application.yaml:46, :62 | ✔ |
| Redis : localhost:6379, SSL, TTL de 15 min | application.yaml:73, :75, :89 | ✔ |
| Docker Compose : postgres:15-alpine, 8090, 80→8082, healthcheck, aucun Redis | docker-compose.yml:5, :28, :38-39, :48 | ✔ |
| Render : port 8080, DATABASE_URL, REDIS_URL, secretEnvVars, PG 15 | backend/render.yaml:9-10, :11-14, :23-26, :27-31, :41 | ✔ |

### Observations hors périmètre de l'Agent 11 (pour information au Tech Lead et à l'Agent 07, sans action de ma part)
- docker-compose.yml:10 et :34 : mot de passe de base de données en clair (valeur non reproduite ici).
- SuperAdminInitializer.java:108-111 : comptes de test avec des mots de passe écrits en dur.
- SecurityConfig.java:118 : adresse IP de réseau local dans les origines CORS.
Ces trois points existaient avant MOD-001.

Écarts à corriger : aucun écart actionnable par l'Agent 11, sauf commiter RENDU-MOD-001.md si cet emplacement est retenu.
Décision humaine requise : oui. Lisibilité des PNG, emplacement de la preuve de rendu, confirmation du 4e fichier de f24c2dc, versionnement des PNG.

VERDICT KASONGO: ESCALADE
