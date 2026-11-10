# APP-BIZ-02 — Chiffrage du projet École 221

> **Auteur** : Agent 08 (Khady Sarr, Business & Marketing). **Date** : 2026-11-09 13:28 (Dakar).
> **Statut** : brouillon à valider par le Tech Lead. Aucune diffusion externe.
> **Réutilisation** : chapitre « Coût du projet » du mémoire, une fois les cases `[À COMPLÉTER PAR L'ÉTUDIANT]` remplies.

## 0. Méthode et légende

- **Fait** : valeur lue dans un fichier du dépôt, avec sa référence `fichier:ligne`.
- `[HYPOTHÈSE]` : estimation, avec son calcul.
- `[À COMPLÉTER PAR L'ÉTUDIANT]` : valeur que je n'ai pas pu vérifier. **Je n'ai pas d'accès web** pendant cette tâche : je n'ai consulté **aucune** page tarifaire officielle. Les URL ci-dessous sont les pages **à consulter**. Il faut noter le prix relevé **et la date de consultation**.
- **À confirmer par le Tech Lead** : offre (gratuite ou payante) que le dépôt ne permet pas de connaître.
- Formule de chaque ligne : `total = quantité × coût unitaire`.
- Conversion : `montant FCFA = montant USD × taux USD/XOF`. Le taux et sa date sont à compléter au § 4.

---

## 1. Hébergement et services : ce que le dépôt montre réellement

### 1.1 Constats (faits)

| Service | Ce que dit le dépôt | Référence |
|---|---|---|
| Render — service web backend (Docker) | `plan: starter` | `backend/render.yaml:2-6` |
| Render — Redis | `plan: starter` | `backend/render.yaml:33-35` |
| Render — PostgreSQL 15 | `plan: starter` | `backend/render.yaml:37-41` |
| Neon (PostgreSQL) | Base désignée comme « base de production » ; le mot de passe de `backend/.env` est refusé | `docs/supervision/SUP-SEC-003.md:58`, `docs/devsecops-pipeline.md:25`, `docs/test-report.md:14` |
| Upstash (Redis) | Mot de passe Upstash présent dans `application.yaml` (valeur par défaut de `REDIS_URL`), à changer | `docs/review-report.md:72` |
| Vercel (frontend) | **Déduit** de l'origine CORS `https://papa-221.vercel.app` ; aucun fichier de configuration Vercel dans le dépôt | `docs/diagrams/README.md:24`, `docs/devsecops-pipeline.md:23` |
| Cloudinary | Clés attendues dans les variables secrètes du backend | `backend/render.yaml:29-31` |
| Local (Docker Compose) | Postgres 15, Redis 7, backend, frontend en local (`127.0.0.1`) : aucun coût d'hébergement | `docker-compose.yml:5-79` |

> ⚠️ **Incohérence à trancher.** `backend/render.yaml` déclare une base PostgreSQL et un Redis **hébergés chez Render** (`plan: starter`). Les autres documents montrent pourtant une base **Neon** et un Redis **Upstash**. Si l'on compte les deux, le coût est compté deux fois. Le chiffrage ci-dessous ne retient **aucun** des deux tant que le Tech Lead n'a pas dit quels services sont réellement provisionnés.
>
> Le libellé `starter` est un nom d'offre Render écrit dans le fichier. Le dépôt ne prouve ni que ce blueprint a été déployé, ni que l'offre est payante. **À confirmer par le Tech Lead.**

### 1.2 Tableau de coûts récurrents d'hébergement

| # | Poste | Offre utilisée | Qté | Coût unitaire (USD/mois) | Total (USD/mois) | Source du prix (page officielle, date de consultation) |
|---|---|---|---|---|---|---|
| H1 | Render — web service backend | `starter` selon `render.yaml:6`. Déploiement réel **à confirmer par le Tech Lead** | 1 | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER PAR L'ÉTUDIANT] | https://render.com/pricing (non consultée) — date : [À COMPLÉTER] |
| H2 | Render — Redis | `starter` selon `render.yaml:35`. Doublon possible avec Upstash : **à confirmer par le Tech Lead** | 1 ou 0 | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER PAR L'ÉTUDIANT] | https://render.com/pricing (non consultée) — date : [À COMPLÉTER] |
| H3 | Render — PostgreSQL | `starter` selon `render.yaml:39`. Doublon possible avec Neon : **à confirmer par le Tech Lead** | 1 ou 0 | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER PAR L'ÉTUDIANT] | https://render.com/pricing (non consultée) — date : [À COMPLÉTER] |
| H4 | Neon — PostgreSQL | Offre inconnue (gratuite ou payante) : **à confirmer par le Tech Lead** | 1 | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER PAR L'ÉTUDIANT] | https://neon.com/pricing (non consultée) — date : [À COMPLÉTER] |
| H5 | Upstash — Redis | Offre inconnue : **à confirmer par le Tech Lead** | 1 | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER PAR L'ÉTUDIANT] | https://upstash.com/pricing (non consultée) — date : [À COMPLÉTER] |
| H6 | Vercel — frontend | Hébergement déduit, offre inconnue : **à confirmer par le Tech Lead** | 1 | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER PAR L'ÉTUDIANT] | https://vercel.com/pricing (non consultée) — date : [À COMPLÉTER] |
| H7 | Cloudinary — stockage de médias | Offre inconnue : **à confirmer par le Tech Lead** | 1 | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER PAR L'ÉTUDIANT] | https://cloudinary.com/pricing (non consultée) — date : [À COMPLÉTER] |
| H8 | Nom de domaine | Le dépôt ne montre aucun domaine propre (seulement un sous-domaine `vercel.app`) | [À COMPLÉTER] | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER PAR L'ÉTUDIANT] | Registraire choisi — date : [À COMPLÉTER] |
| | **Sous-total hébergement mensuel** | | | | **[À COMPLÉTER] = somme de H1 à H8** | |
| | **Sous-total hébergement annuel** | | | | **[À COMPLÉTER] = sous-total mensuel × 12**, ou tarif annuel publié s'il existe | |

> Si une offre se révèle gratuite, écrire `0` avec la source et sa date. Ne pas laisser la case vide.

---

## 2. Coûts IA réels des agents (pipeline multi-agents)

### 2.1 Méthode (faits)

- Source : champ `cout_total` de la ligne `"evenement": "fin"` de chaque fichier `logs/agent_runs/*.jsonl`. Cette ligne est écrite à la clôture du run (`orchestration/agent_runtime.py:368`). J'ai vérifié pour `20261108-185219-agent00.jsonl:10` qu'il s'agit bien de la dernière ligne.
- **Unité : dollar US.** Le budget est exprimé en dollars (`orchestration/agent_runtime.py:12`, `:254`).
- ⚠️ **Il s'agit d'un coût calculé, pas facturé.** Le moteur l'obtient à partir d'une table de prix écrite dans le code (`orchestration/agent_runtime.py:29-30`, « $ par million de jetons », modèle `claude-opus-5-5` : 4,00 en entrée, 20,00 en sortie, 0,20 en lecture de cache, 5,00 en écriture de cache). Ce n'est pas une page tarifaire officielle. Le montant réellement facturé est à confirmer sur la facture ou la console du fournisseur : [À COMPLÉTER PAR L'ÉTUDIANT].
- **Exclus** : les 5 runs lancés à `20261109-132833` (agents 01, 06, 07, 08, 11) sont encore en cours au moment de la rédaction et n'ont pas de ligne `fin`. Leur coût est à ajouter après clôture.

### 2.2 Détail des 19 runs clôturés

| Fichier | Agent | Statut | `cout_total` (USD) |
|---|---|---|---|
| 20261108-185219-agent00 | 00 | BUDGET_ATTEINT | 0,54044 |
| 20261108-185337-agent00 | 00 | PARTIEL | 0,40576 |
| 20261108-191357-agent11 | 11 | PARTIEL | 0,51322 |
| 20261108-191839-agent00 | 00 | TERMINE | 0,40776 |
| 20261108-192042-agent11 | 11 | ESCALADE | 0,21828 |
| 20261108-192224-agent00 | 00 | ESCALADE | 0,29407 |
| 20261109-100550-agent09 | 09 | TERMINE | 0,99076 |
| 20261109-101036-agent00 | 00 | TERMINE | 0,53821 |
| 20261109-101316-agent09 | 09 | ESCALADE | 0,50408 |
| 20261109-101509-agent00 | 00 | ESCALADE | 0,49863 |
| 20261109-105529-agent09 | 09 | PARTIEL | 1,40300 |
| 20261109-110152-agent00 | 00 | ESCALADE | 0,77538 |
| 20261109-110628-agent03 | 03 | TERMINE | 0,77318 |
| 20261109-114340-agent03 | 03 | TERMINE | 1,03308 |
| 20261109-124206-agent05 | 05 | PARTIEL | 1,48776 |
| 20261109-125045-agent05 | 05 | TERMINE | 0,83656 |
| 20261109-130530-agent03 | 03 | TERMINE | 0,56249 |
| 20261109-130530-agent04 | 04 | TERMINE | 0,36603 |
| 20261109-131402-agent02 | 02 | TERMINE | 1,34747 |
| **Total (19 runs)** | | | **13,49616** |

### 2.3 Synthèse par agent

| Agent | Nombre de runs | Coût total (USD) |
|---|---|---|
| 00 | 7 | 3,46025 |
| 09 | 3 | 2,89784 |
| 03 | 3 | 2,36875 |
| 05 | 2 | 2,32432 |
| 02 | 1 | 1,34747 |
| 11 | 2 | 0,73150 |
| 04 | 1 | 0,36603 |
| **Total** | **19** | **13,49616** |

Contrôle : 3,46025 + 2,89784 + 2,36875 + 2,32432 + 1,34747 + 0,73150 + 0,36603 = 13,49616 USD.

### 2.4 Limites

- Les journaux ne couvrent que la période du 2026-11-08 18:52 au 2026-11-09 13:19. L'IA utilisée avant cette période n'est pas comptée : le dossier `.kilo/` laisse supposer un autre outil, et des abonnements d'assistants de code ont peut-être été payés. Montant : [À COMPLÉTER PAR L'ÉTUDIANT].
- `[HYPOTHÈSE]` Coût IA moyen par run = 13,49616 ÷ 19 ≈ **0,71 USD**. Cette moyenne sert seulement d'ordre de grandeur pour estimer de futurs runs (`nombre de runs prévus × 0,71`). Ce n'est pas un engagement.

---

## 3. Ressources humaines `[HYPOTHÈSE]`

Je n'ai trouvé dans le dépôt aucun relevé d'heures ni aucun taux horaire. Toutes les valeurs restent donc à compléter. La structure de calcul est proposée.

| # | Rôle | Qté (personnes) | Volume (heures ou jours) | Coût unitaire (FCFA/h ou /jour) | Total (FCFA) | Source / justification |
|---|---|---|---|---|---|---|
| R1 | Étudiant·e développeur·se / Tech Lead | [À COMPLÉTER] | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER PAR L'ÉTUDIANT] `[HYPOTHÈSE]` | = Qté × Volume × Coût unitaire | Grille de référence à citer (convention de stage, grille salariale publiée) avec sa date |
| R2 | Encadrement (tuteur, maître de stage) | [À COMPLÉTER] | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER PAR L'ÉTUDIANT] `[HYPOTHÈSE]` | = Qté × Volume × Coût unitaire | Idem |
| | **Sous-total RH (initial)** | | | | **[À COMPLÉTER]** | |

> Si le travail n'est pas rémunéré (projet académique), on peut valoriser les heures à un taux de marché, c'est-à-dire un **coût d'opportunité**. Il faut alors le dire explicitement et citer la source du taux. Il faut aussi préciser si ce coût entre dans le total ou s'il est seulement présenté pour information.

---

## 4. Taux de change

| Élément | Valeur | Source | Date |
|---|---|---|---|
| Taux USD → XOF (FCFA) | [À COMPLÉTER PAR L'ÉTUDIANT] | Cours publié par la BCEAO (bceao.int) ou une autre source officielle, à citer | [À COMPLÉTER] |
| Repère : parité EUR → XOF | Parité fixe (1 EUR = 655,957 XOF), à vérifier et citer sur bceao.int | [À COMPLÉTER] | [À COMPLÉTER] |

Exemple de conversion (formule) : coût IA en FCFA = 13,49616 × taux USD/XOF = **[À COMPLÉTER]**.

---

## 5. Récapitulatif

| Bloc | Nature | USD | FCFA | Statut |
|---|---|---|---|---|
| Coûts IA des agents (19 runs clôturés) | Initial (développement) | **13,49616** (coût calculé) | = 13,49616 × taux § 4 → [À COMPLÉTER] | Fait (journaux) ; facture à confirmer |
| Coûts IA hors journaux (autres outils et abonnements) | Initial | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER] | Inconnu |
| Ressources humaines | Initial | [À COMPLÉTER] | [À COMPLÉTER PAR L'ÉTUDIANT] | `[HYPOTHÈSE]` |
| Matériel et connexion internet (poste de développement) | Initial | [À COMPLÉTER PAR L'ÉTUDIANT] | [À COMPLÉTER] | Inconnu |
| **Total initial** | | **13,49616 + [À COMPLÉTER]** | **[À COMPLÉTER]** | Incomplet |
| Hébergement et services (H1 à H8) | Récurrent mensuel | [À COMPLÉTER] | [À COMPLÉTER] | Offres à confirmer par le Tech Lead |
| IA en exploitation (si les agents continuent après la livraison) | Récurrent mensuel | `[HYPOTHÈSE]` nombre de runs par mois × 0,71 → [À COMPLÉTER] | [À COMPLÉTER] | `[HYPOTHÈSE]` |
| **Total récurrent mensuel** | | **[À COMPLÉTER]** | **[À COMPLÉTER]** | Incomplet |
| **Total récurrent annuel** | | **= total mensuel × 12** → [À COMPLÉTER] | [À COMPLÉTER] | Incomplet |

---

## ❓ Points à valider par le Tech Lead

1. **Infrastructure réellement en service.** `backend/render.yaml` (Postgres et Redis chez Render, `plan: starter`) contredit les documents qui citent Neon et Upstash. Quels services sont réellement provisionnés et facturés ? Le blueprint Render a-t-il été déployé ?
2. **Offres utilisées** chez Render, Neon, Upstash, Vercel et Cloudinary : gratuites ou payantes ? Le dépôt ne permet pas de le savoir.
3. **Prix publics** : il faut relever les prix sur les pages officielles en notant la date de consultation. Je n'avais pas d'accès web.
4. **Coût IA** : 13,49616 USD est un coût **calculé** avec la table de prix codée en dur (`agent_runtime.py:29-30`). Il faut confirmer ce montant avec la facture ou la console du fournisseur, et indiquer si d'autres outils d'IA ont été payés avant le 2026-11-08.
5. **Taux USD/XOF** : choisir la source et la date du taux.
6. **Ressources humaines** : faut-il valoriser les heures étudiantes (coût d'opportunité) ou les exclure du total ?
7. **Nom du fichier** : la fiche de poste prévoit le format `docs/business/BIZ-XXX-[sujet].md`, mais le brief demande `docs/business/chiffrage.md`. J'ai suivi le brief. Faut-il renommer le fichier, par exemple en `BIZ-002-chiffrage.md` ?
8. **Sécurité (hors chiffrage, rappel)** : `docs/review-report.md:72` signale un mot de passe Upstash commité, qui reste à changer. Ce point n'a pas d'impact sur les coûts, mais il bloque tout discours commercial sur la sécurité.
