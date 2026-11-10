# Notes de version du 9 novembre 2026 : PROPOSÉ, NON DÉPLOYÉ

- **Auteur** : Agent 10 (Ibrahima Guèye, Release & CI/CD). Document rédigé par Claude, **à valider par le Tech Lead**.
- **Date** : 2026-11-09 13:58 (Dakar). Cette version remplace le brouillon commité en `096b33f`.
- **Statut** : **proposé, non déployé**. Rien n'a été poussé, fusionné ni déployé. **Aucune exécution CI n'est associée à ce document** : les pipelines `615cf36` (backend) et `6f87311` (frontend) existent sous forme de commits, mais aucune exécution (lien, identifiant, statut) n'a été fournie.
- **Verdicts en vigueur** : revue Agent 06 **`VERDICT: REJECTED`** (`docs/review-report.md:61`, `:171`) ; DevSecOps **`VERDICT DEVSECOPS: NO-GO`** (`docs/devsecops-pipeline.md:28`, confirmé l.174). **Aucun déploiement n'est donc possible en l'état** (fiche 10, frontière 1).

## Source de la traçabilité

- `git-log-jour` (exécutée le 2026-11-09 vers 13:58, code 0) : commits du jour des 3 dépôts. **Chaque ligne ci-dessous correspond à un commit de cette sortie.** Le libellé « Changement » reprend le message du commit. Je ne l'ai **pas** vérifié par un diff, que je ne peux pas exécuter. Quand le code courant le confirme, la colonne « Preuve » cite fichier:ligne.
- **Têtes livrables** : backend `362550f`, frontend `8c5b9ad`, racine `1c25fa0`. Le commit `1c25fa0` enregistre ces sous-modules d'après son message.
- **Plage revue par l'Agent 06** : backend `974b36d..5149cfa`, frontend `89ff3e0..f2a8c2d` (`docs/review-report.md:6`). Les commits marqués **(hors revue)** sont postérieurs à cette plage, ou en sont la borne exclue (`89ff3e0`). **Ils n'ont pas été revus.**
- **Réserve** : `git-status` (13:58, code 0) renvoie encore ` m backend` et ` m frontend`. Les sous-modules contiennent donc du contenu modifié non commité. **Ce contenu ne fait pas partie de la version** : tout artefact doit être construit à partir des SHA ci-dessus, et non depuis l'arbre de travail.

---

## 1. Changements par dépôt (une ligne = un commit)

### Backend (25 commits, du plus ancien au plus récent)

| Hash | Catégorie | Carte | Changement | Preuve / remarque |
|---|---|---|---|---|
| `722086e` | Sécurité | APP-SEC-02 / APP-SEC-01 | Secret JWT obligatoire ; WebSocket limité aux origines CORS | `JwtService.java:44-56` ; `application.yaml:143` |
| `cd033c4` | Outillage | APP-BE-01 | Suite de tests 113/113 | message du commit |
| `05874e2` | Sécurité | APP-SEC-03 / APP-SEC-10 | Comptes de démonstration désactivés par défaut | `SuperAdminInitializer.java:63-72` ; `DataInitializer.java:431-433` |
| `615cf36` | Outillage | APP-CI-01 | Pipeline GitHub Actions du backend (**jamais exécuté à ma connaissance**) | — |
| `21970b1` | Fonctionnel | APP-BE-16 | Identité du professeur issue de l'authentification | review l.42 |
| `9d2211f` | Sécurité | APP-SEC-09 | Spring Boot 4.1.2 et httpclient 4.5.14 | review l.24 |
| `44cc42f` | Fonctionnel | APP-BE-04 | Plus aucun paiement ni reçu fictif | bus l.451-471 |
| `282ee35` | Sécurité | APP-SEC-04 | Origines configurables par `CORS_ALLOWED_ORIGINS` (joker `*` refusé) | `AllowedOrigins.java:11-39` |
| `0f10eee` | Sécurité | APP-SEC-12 | Admissions et candidatures fermées au public, **sauf `/admissions/db`, qui reste anonyme** (voir §3) | `SecurityConfig.java:73-74,82-83` |
| `02a4f3c` | Sécurité | APP-SEC-12 | Retrait des 21 `@CrossOrigin("*")` des contrôleurs | message du commit |
| `e9a661a` | Sécurité | APP-SEC-11 | `/parent/**` réservé au rôle PARENT ; identité tirée de l'authentification | review l.26 |
| `98216e4` | Outillage | APP-SEC-03 | Plus de mot de passe littéral dans les 14 scripts historiques (lecture de `DEMO_ACCOUNTS_PASSWORD`) | `backend/test_all_roles.sh:11` |
| `1976c72` | Sécurité | APP-SEC-13 | Plus de mot de passe ni de données personnelles dans les journaux | review l.34 |
| `233019a` | Outillage | APP-BE-02 | Tests d'intégration SEC-003 de bout en bout | review l.40 |
| `757bc9e` | Fonctionnel | US-02 (OBS-01) | `POST /register-school` renvoie 201 | `PublicOnboardingController.java:35-36` |
| `c54c892` | Fonctionnel | OBS-02 | Note mal nommée ou hors 0–20 refusée (400) ; moyenne arrondie | `ProfessorController.java:383,389` |
| `2f34e62` | Fonctionnel | APP-BE-18 | `GET /parent/paiements` sans paiements inventés | review l.44 ; bus l.566-582 |
| `cd421c1` | Sécurité | APP-BE-19 | Un parent ne voit plus que ses enfants réels | review l.46 |
| `5149cfa` | Sécurité | APP-SEC-14 | Rendez-vous : plus de fuite entre familles ni de rendez-vous inventé | review l.38 |
| `16de9bd` | Sécurité | APP-SEC-05 | Mot de passe de la base retiré de `application-dev.yaml` ; jarres de cookies désindexées **(hors revue)** | `application-dev.yaml:8` (le commentaire du code cite APP-TL-14) |
| `1085787` | Fonctionnel | APP-BE-19 | Notes de l'enfant lues dans les notes réellement saisies **(hors revue)** | message du commit |
| `6fd98a6` | Sécurité | APP-SEC-15 | Collaboration, wiki, notifications, sync et médias fermés aux visiteurs sans compte **(hors revue)** | `SecurityConfig.java:63-64` |
| `751a9d1` | Sécurité | APP-SEC-16 | Un professeur n'annule ou ne reporte que ses propres séances **(hors revue)** | message du commit |
| `76d3af5` | Sécurité | APP-SEC-15 | Envoi public de fichiers (`POST /media/upload`) : signature réelle, débit limité, 400 au lieu de 500 **(hors revue)** | `SecurityConfig.java:64,81` (la route reste publique) |
| `362550f` | Fonctionnel | — | Notes : saisir une seule note n'efface plus l'autre **(hors revue)** | message du commit |

### Frontend (7 commits)

| Hash | Catégorie | Carte | Changement | Preuve / remarque |
|---|---|---|---|---|
| `89ff3e0` | Fonctionnel | APP-ARC-01 | 14 appels frontend alignés sur les routes réelles du backend. **(Borne exclue de la plage revue.)** | message du commit |
| `6f87311` | Outillage | APP-CI-02 | Pipeline frontend (typage, build, lint, audit, gitleaks). **Jamais exécuté à ma connaissance**, et le job d'audit n'est pas bloquant | review l.22 |
| `3606bb6` | Sécurité | APP-SEC-08 | `npm audit` prod : 1 critique + 9 hautes ramenées à **1 haute (xlsx), toujours présente** | review l.22 |
| `aa68167` | Sécurité | APP-SEC-03 | Plus d'identifiants de démo sur la page de connexion en production (`VITE_DEMO_LOGIN`) | `LoginForm.tsx:41-42` |
| `b6f3227` | Fonctionnel | APP-FE-04 | Profil 360 : plus de faux reçus, mention « non disponible » explicite | message du commit |
| `f2a8c2d` | Fonctionnel | APP-FE-05 | Page Paiements parent sans enfant ni reçu inventés | bus l.543-563 ; review l.48 |
| `8c5b9ad` | Fonctionnel | APP-FE-06 | Parent (notes, présences, planning, messages) : plus de données inventées en repli ; `ChildGrade` accepte `null` **(hors revue)** | bus l.718-735 |

### Racine (commits liés à la livraison applicative)

| Hash | Catégorie | Carte | Changement |
|---|---|---|---|
| `7bb6b2a` | Outillage | BE-003 | Bus : livraison APP-SEC-01/02 |
| `2639ecd` | Infra | APP-SEC-06 | `docker-compose` durci |
| `97fbbd3` | Sécurité | APP-SEC-09 | Contrôle des dépendances Maven (SBOM + osv-scanner) |
| `9347ce9` | Infra | APP-SEC-06 | Port frontend sur 127.0.0.1 ; contrôle compose fiabilisé |
| `1d76b66` | Outillage | APP-BE-04 / APP-SEC-04 | Sous-module backend ; `CORS_ALLOWED_ORIGINS` documentée (`.env.example:7`) |
| `5e0f7c9` | QA | APP-SEC-12 | 8 contrôles d'accès sans compte sur les admissions |
| `d1d3bc7` | Outillage | APP-SEC-12 | Sous-module backend (`@CrossOrigin` retirés) |
| `5397304` | QA | APP-SEC-11 | `/parent/**` : 403 pour l'ADMIN, 401 sans compte |
| `7a0d9c4` | Outillage | APP-CI-02 | Sous-module frontend (pipeline) |
| `6140a8a` | Outillage | APP-SEC-08 | Sous-module frontend (dépendances npm) |
| `e204f67` | Audit | — | Contrôle « mots de passe en dur » : scripts historiques nettoyés, tests unitaires exclus |
| `df42445` | Outillage | APP-SEC-03 | Sous-module frontend (connexion rapide réservée au dev) |
| `b8c935d` | Audit | — | Preuves : 7 PASS / 3 FAIL |
| `d84a022` | Outillage | APP-SEC-13 | Sous-module backend (journaux masqués) |
| `0af7a6d` | QA | APP-QA-01 | Exigences citées dans les scripts QA |
| `c6ba5e0` | Gouvernance | APP-BE-02 | Périmètre de l'Agent 05 élargi à `docs/qa/` ; sous-module backend |
| `22c5c6d` | QA | US-02 | 201 vérifié sur `POST /register-school` ; sous-module backend (`757bc9e`) |
| `52e4204` | QA | OBS-02 | Notes envoyées avec les clés du contrat et vérifiées |
| `8b1b2bd` | QA | APP-QA-01 | Matrice de traçabilité exigences → tests |
| `64408f1` | Outillage | APP-FE-04 | Sous-module frontend |
| `7b08671` | Infra | APP-ARC-05 | Redis dans `docker-compose` |
| `4a56cf2` | QA | APP-BE-18 / APP-FE-05 | Sous-modules ; QA parent : paiements non fictifs vérifiés |
| `847e189` | QA | APP-BE-19 | Élève de test relié au parent ; enfant d'une autre famille refusé |
| `a3f2832` | Contrat | APP-ARC-06 | §2.6 « Espace Parent » (16 routes `/api/parent/**`), statut IN_REVIEW |
| `5b7f012` | Outillage | APP-SEC-14 | Sous-module backend (rendez-vous parent) |
| `7d9c266` | Audit | — | Preuves de fin de journée : 7 PASS / 3 FAIL ; QA 16/16 |
| `e54183d` | Outillage | — | Moteur d'agents robuste ; contrôle des mots de passe YAML non cités |
| `eae9a09` | Sécurité | APP-SEC-05 | Plan de purge de l'historique, **sans exécution** |
| `7c5b81e` | Outillage | APP-BE-19 / APP-SEC-05 | Bus ; QA parent ; sous-module backend |
| `98357df` | Outillage | APP-SEC-15 / APP-REV-01 | Sous-module + QA ; revue APP-REV-01 ; commandes git en lecture pour les agents 00, 05 et 06 |
| `294ef02` | Outillage | APP-SEC-16 | Sous-module backend (séances du professeur) |
| `8ecac91` | Audit | APP-SEC-05/15/16 | Preuves après correctifs (contrôle YAML ajouté) ; QA 16/16 |
| `39e683f` | Audit | — | Preuves de fin de série (QA 16/16 relancée avant collecte) |
| `096b33f` | Docs | REL-001 | Brouillon de ces notes (avec MEM-12 et FEAT-003 en DRAFT) |
| `1c25fa0` | Outillage | — | Sous-modules (upload sécurisé, notes partielles, APP-FE-06) ; bus |

**Commits racine du jour hors livraison applicative** (mémoire, exigences, chiffrage, orchestration). Ils sont listés pour que la sortie de `git-log-jour` soit couverte en entier ; ils n'entrent pas dans l'artefact déployé :

| Hash | Objet |
|---|---|
| `8c42ea6` | Exigences FEAT-006 (DRAFT), FEAT-002 à 005 corrigées |
| `6895cca` | APP-BIZ-02 : chiffrage partiel |
| `4d21923` | MEM-09 / MEM-10 : diagrammes |
| `9e9b944` | MEM-21 : journal d'usage de l'IA |
| `cc1cd0a` | DOC-002 : écarts corrigés |
| `bfb126b` | DOC-002 : introduction et §8.5 |
| `b823340` | Mémoire : Licence Pro et titre |
| `8fc6397` | Mémoire : normes de présentation |
| `a27c491` | Mémoire : page de garde |
| `17ddfcd` | Mémoire : habillage des pages |
| `2ac3ef6` | Mémoire : pages de partie et sommaire |
| `322fdbf` | Mémoire : visuel de page de garde |
| `fe8ffad` | Mémoire : informations de l'étudiant |
| `7a4b146` | Orchestration : sortie non UTF-8 |
| `918cc4b` | DOC-001 : corrections après convocation |
| `bd71c29` | DOC-001 : contrôle Kasongo |
| `bbca0c9` | Orchestration : recompilation par Kasongo |
| `b45851f` | MEM-01 : squelette du mémoire |
| `893882e` | Orchestration : commit de départ choisi par Kasongo |
| `c63a41d` | Modèle LaTeX et canevas |
| `2839728` | Orchestration : commande `memoire-build` |

---

## 2. Variables d'environnement à définir avant déploiement

Aucune valeur n'est donnée ici : elles se déclarent dans les secrets Render, Vercel ou GitHub Actions.

| Variable | Dépôt | Caractère | Comportement | Preuve (commit) |
|---|---|---|---|---|
| **`JWT_SECRET`** | backend | **obligatoire partout** | Si la variable est absente, fait moins de 32 caractères ou reprend l'ancienne valeur publique, **l'application ne démarre pas**. Son changement est aussi exigé par SEC-ALERT-006 | `JwtService.java:44-56` ; `application.yaml:143` ; bus l.440, l.643 (`722086e`) |
| `DATABASE_PASSWORD` | backend | obligatoire avec le profil dev | `${DATABASE_PASSWORD}` sans valeur par défaut. Remarque : le profil par défaut utilise `${DATABASE_PASSWORD:}`, donc une valeur vide est acceptée au démarrage | `application-dev.yaml:8` ; `application.yaml:30` ; `render.yaml:19` (`16de9bd`) |
| `CORS_ALLOWED_ORIGINS` | backend | facultatif, **à définir en production** | Défaut : `localhost` + `https://papa-221.vercel.app`. Le joker `*` est refusé. Le défaut garde `http://localhost:*` avec `allowCredentials=true` (MINOR, review l.20) | `AllowedOrigins.java:17-39` (`282ee35`) |
| `VITE_DEMO_LOGIN` / `VITE_DEMO_PASSWORD` | frontend (au build) | facultatifs | Absents : la connexion rapide est désactivée **en build de production**. Elle reste active en mode `DEV` quelle que soit la valeur. ⚠️ **Une variable `VITE_*` est intégrée en clair dans le bundle JS publié.** Ne jamais définir `VITE_DEMO_PASSWORD` sur un build public | `LoginForm.tsx:41-42` ; `frontend/.env.example:27` (`aa68167`) |
| `DEMO_ACCOUNTS_PASSWORD` / `ECOLE_DEMO_ACCOUNTS_ENABLED` | scripts **et backend** | facultatifs ; **à ne pas activer en production** (APP-TL-09) | `DataInitializer` lève une exception si les comptes de démo sont demandés sans un mot de passe d'au moins 12 caractères. `SuperAdminInitializer` n'agit qu'avec `ECOLE_DEMO_ACCOUNTS_ENABLED=true` | `DataInitializer.java:431-433` ; `SuperAdminInitializer.java:63-72` (`05874e2`, `98216e4`) |

---

## 3. Changements de contrat visibles

| Changement | État constaté dans le code | Commit |
|---|---|---|
| `POST /register-school` → **201** au lieu de 200 | Présent (`PublicOnboardingController.java:36`). La QA le vérifie d'après le message de `22c5c6d` | `757bc9e` |
| Notes invalides → **400** ; moyenne arrondie | Présent (`ProfessorController.java:383,389`). Vérifié par la QA d'après le message de `52e4204` | `c54c892` |
| Saisie d'une seule note : l'autre n'est plus effacée | Changement de comportement d'après le message ; non vérifié par diff ni par QA | `362550f` |
| `GET /parent/paiements` : nouveau champ **`statut`** (`non_disponible` / `disponible`), `echeances: []` | Présent ; contrat §2.6 en IN_REVIEW (`a3f2832`) | `2f34e62` |
| Notes de l'enfant côté parent : `cc`, `examen`, `moyenne`, `ects` et `mention` peuvent valoir `null` | Annoncé par l'Agent 04 (bus l.730, en lien avec `1085787`) ; le frontend s'y adapte | `1085787` (backend), `8c5b9ad` (frontend) |
| `/admissions/**` authentifié **sauf portail** | ⚠️ **Partiel** : **`/admissions/db` (GET et POST) reste public** (`SecurityConfig.java:73-74,82-83`, « TEMPORAIRE (carte APP-TL-10) »). C'est le motif CRITICAL du REJECTED (`review-report.md:63`). **On ne peut pas annoncer que la route est authentifiée** | `0f10eee` |
| `/collaboration`, `/wiki`, `/notifications`, `/sync`, `/media` authentifiés | Présent (`SecurityConfig.java:63-64`) ; non revu | `6fd98a6` |
| Exceptions restées publiques : `GET /sync/check` et `POST /media/upload` ; l'upload renvoie désormais 400 au lieu de 500 et son débit est limité | `SecurityConfig.java:64,72,81` ; non revu | `6fd98a6`, `76d3af5` |
| Réponses de `/admissions/db` et de profile360 : `paymentMethod` et `cniUrl` à `null`, `cniStatus: "unknown"`, `paymentsStatus` | Annoncé par APP-BE-04 (bus l.462-467) ; ces routes ne figurent pas dans le contrat | `44cc42f` |

---

## 4. Actions Tech Lead préalables

Les intitulés viennent de la tâche du Tech Lead (13:58). Les cartes 09 et 12 n'ont toujours aucune occurrence écrite dans le dépôt (bus l.713). Les actions détaillées ci-dessous sont des **propositions**.

| Carte | Intitulé | Lien avec la version | Proposition (non exécutée) |
|---|---|---|---|
| **APP-TL-09** | Comptes de démo en production | `05874e2` désactive ces comptes **par défaut** dans le code. Cela ne supprime pas les comptes déjà créés en base de production | Vérifier que `ECOLE_DEMO_ACCOUNTS_ENABLED` n'est pas à `true` sur Render, puis inventorier et neutraliser les comptes de démo existants dans la base de production (décision et exécution : Tech Lead) |
| **APP-TL-12** | Mots de passe dans les journaux Render | `1976c72` (APP-SEC-13) masque les **futurs** journaux. Les journaux déjà émis ne sont pas traités | Purger ou limiter la rétention des journaux Render existants ; changer tout mot de passe qui y figure |
| **APP-TL-14** | Révoquer le mot de passe Neon | `16de9bd` retire le mot de passe de `application-dev.yaml` ; il reste dans l'historique (plan de purge `eae9a09`, **non exécuté**) | **Réinitialiser le mot de passe Neon** (`neondb_owner`) et **changer `JWT_SECRET`** avant toute purge (SEC-ALERT-006, CRITICAL, bus l.628-644) |

Autres préalables : décision sur **APP-TL-10** (`/admissions/db` public, bloquant pour la revue) ; levée d'APP-REV-01 ; passage de `NO-GO` à `GO` DevSecOps ; revue des commits marqués « hors revue ».

---

## 5. Ordre de déploiement conseillé et retour arrière (proposition, non exécutée)

**Préalables** : APP-REV-01 levé, `VERDICT DEVSECOPS: GO`, actions du §4 faites, CI exécutée et verte sur `362550f` / `8c5b9ad` (lien à fournir), accord explicite du Tech Lead.

1. **Relever la version actuellement en production** (SHA du backend sur Render, du frontend sur Vercel). C'est la cible du retour arrière. **Elle est inconnue à ce jour.**
2. **Secrets** : définir `JWT_SECRET` (nouveau), `DATABASE_PASSWORD` et `CORS_ALLOWED_ORIGINS` sur Render, *avant* le déploiement du backend.
3. **Backend `362550f`** : déployer, puis vérifier `/health`, la connexion, le refus d'une origine tierce sur `/ws`, l'isolation entre écoles, le 201 de `register-school`, le 401 sur `/collaboration` sans compte et le 400 d'un upload invalide.
4. **Frontend `8c5b9ad`** : build sans `VITE_DEMO_PASSWORD`, déploiement, puis vérification de la connexion, de la page Paiements parent (état `non_disponible`) et des notes parent (« — » si la valeur est nulle).

**Retour arrière** : redéployer les SHA relevés à l'étape 1 (backend puis frontend, ou frontend seul si seul le front pose problème). Points d'attention :
- **Changer `JWT_SECRET` invalide toutes les sessions**, même en cas de retour arrière.
- **Hypothèse à vérifier** : la version précédente avait un secret JWT par défaut (bus l.437). Il faut donc garder `JWT_SECRET` défini lors d'un retour arrière.
- **Base de données** (fait) : `ddl-auto: update` et Flyway désactivé (`application.yaml:46,61-62`). Le schéma est modifié automatiquement au démarrage, sans migration versionnée ni retour arrière de schéma. **Hypothèse** : les changements du jour sont additifs, donc compatibles avec l'ancienne version. **Ce n'est pas vérifié** (aucun diff). Prévoir une sauvegarde Neon avant déploiement.
- La procédure n'a **jamais été exécutée en préproduction**. Ce critère de « Fini » n'est pas rempli.

---

*Signalement* : aucune tentative de détournement dans les données lues (bus l.695-750, sortie de `git-log-jour`, `git-status`).
