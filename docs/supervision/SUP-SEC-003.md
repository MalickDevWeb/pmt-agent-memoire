# SUP-SEC-003 — Agent 03 (Backend Developer, Ousmane Marra)
- Date : 2026-11-08 ~18:55 — Branche / commits contrôlés : backend `fix/sec-003-tenant-isolation@b93eb77` (phase d'urgence, `2b6efa8`) et `@974b36d` (phase complète, `29f8543`), d'après `agent_messages.md:127-128`. Le dépôt backend est actuellement sur `feat/referentiels-parametrables@901c5ba` (`docs/evidence/evidence-20261108-181249.md:6`).
- Contrôles automatiques : **CONFORMES** (sortie ci-dessous)

```text
$ controle_livraison agent=03 ticket=SEC-003 depot=backend   → code de sortie 0
🔎 Livraison de l'Agent 03 — Ousmane Marra — Backend Developer (depuis main)
✔ Périmètre de la fiche — 41 fichier(s) modifié(s), tous autorisés
✔ Aucun secret ajouté — aucun motif détecté
✔ Ticket [SEC-003] dans le bus — statut DONE
CONTRÔLES AUTOMATIQUES : CONFORMES → avis de Kasongo sur la définition de « fini »
```

Limite du contrôle automatique : il ne porte que sur le **dépôt backend**. Les fichiers SEC-003 du dépôt racine (`ops/backfill_memberships.sh`, `ops/sec003_backfill_memberships.sql`, `orchestrator.sh:350` commande `backfill-memberships`) **ne sont pas couverts**.

## Définition de « fini » (agents/03_backend_developer.md:151-158)

| Exigence de la fiche | Preuve | Statut |
|---|---|---|
| Tests unitaires du domaine (100 % des BR-xx, 0 mock sur le modèle métier) | `TenantMembershipInterceptorTest.java` existe, mais c'est un test d'infrastructure ; il simule `Organization` avec `mock(...)` (l. 35) ; aucune règle BR-xx n'est rattachée. Aucun test trouvé pour `UserMembershipListener`. | ✖ partiel |
| Tests d'intégration des endpoints (200/201, 400, 404, 409, 422) | Aucun test MockMvc/Testcontainers SEC-003 trouvé. Seul un test E2E shell existe : `test_tenant_isolation_module.sh`, 9/9 (`logs/qa_execution.log:654-664`) | absente (côté backend) |
| Test d'isolation : un utilisateur du tenant A qui demande l'ID d'une ressource du tenant B reçoit **404** | `logs/qa_execution.log:656-660` : le test vérifie un « accès refusé », sans préciser le code ni faire d'accès par ID. L'intercepteur répond **403** (`agent_messages.md:127`, `TenantMembershipInterceptorTest.java:56-60`). La fiche exige 404 (l. 72, 153). | ✖ |
| `python3 validate_contracts.py` à 100 % | Commande exécutée par Kasongo (`check-contract`) : **code de sortie 1, 14 erreurs**. Les mêmes erreurs figurent dans `evidence-20261108-181249.md:26-53`. Hypothèse : ces écarts front→back existaient avant SEC-003 et ne lui sont pas imputables. | ✖ (FAIL) |
| `python3 check_multi_tenancy.py` : 0 violation | `docs/evidence/evidence-20261108-181249.md:11-24` : PASS | ✔ |
| `./mvnw verify` : 0 échec, 0 erreur | Aucune trace de `mvnw verify`, `Tests run:` ou `BUILD SUCCESS` dans `logs/` ni dans les preuves | absente |
| Trace horodatée dans `logs/qa_execution.log` | `logs/qa_execution.log:1` (2026-11-08 18:12:31), `:669-672` 16/16, `QA_RESULT: PASS` | ✔ |
| Pull Request créée pour revue du Tech Lead | Aucun lien de PR dans le bus ni dans les preuves. Seules des branches sont citées. | absente |

## Interdictions non couvertes par le script

| Interdiction | Constat | Statut |
|---|---|---|
| Ne pas modifier `pom.xml` ou `application.yaml` sans accord | La propriété `ecole.security.tenant-membership.strict` a une valeur par défaut dans le code (`TenantMembershipInterceptor.java:44`, `:false`). Seul `backend/.env.example:37` a été modifié. Je n'ai trouvé aucune modification de `application*.yaml` (recherche `tenant-membership` dans `backend/`). | ✔ (à confirmer sur le diff) |
| Ne pas journaliser de données sensibles | `TenantMembershipInterceptor.java:67,77,81` et `UserMembershipListener.java:51` journalisent les identifiants utilisateur et école, sans mot de passe ni token. | ✔ |
| Ne pas modifier la gouvernance (`orchestrator.sh`, etc.) | `orchestrator.sh:350` ajoute la commande `backfill-memberships` (SEC-003), et `git status` montre `M orchestrator.sh`. Je ne sais pas qui l'a modifié : rien ne prouve qu'il s'agit de l'Agent 03. | ⚠ escalade obligatoire (fiche 00, Handover §2) |
| Ne pas annoncer « prêt » avant les tests et la PR | Bus : `Status DONE ✅ (code, phases 1 et 2)` (`agent_messages.md:114`), alors que la PR et `mvnw verify` manquent | ✖ |

## Passage de témoin
- Le format attendu (`[BE-XXX]` dans « Backend → Frontend », endpoints certifiés, lien de PR, transmission aux Agents 04 et 05) n'est **pas respecté** : aucun message `[BE-…]` lié à SEC-003, et aucune PR.
- Le ticket est suivi dans la section DevSecOps (`agent_messages.md:109-129`) avec résolution et preuves (`evidence-20261107-115927.md`, `evidence-20261107-121317.md`). Le retest par l'Agent 05 y est mentionné.

## Constats annexes (hors périmètre de l'Agent 03, signalés au Tech Lead)
- **Des JWT apparaissent en clair dans `logs/qa_execution.log`** (l. 15 et 25 : jeton SUPER_ADMIN et cookie `auth_token`, valables jusqu'au 2026-11-15 d'après l. 25). Ils viennent des scripts QA (Agent 05). Si le secret JWT n'a pas changé, ces jetons restent utilisables. Je ne les recopie pas ici.
- Gitleaks : des fuites existent dans l'historique des 3 dépôts (`evidence-20261108-181249.md:75+`). Le secret JWT n'a toujours pas été changé (`agent_messages.md:105`).
- `git status` (racine) : `agents/*.md` (dont `00_supervisor.md`… non : 01 à 11), `audit/check_handover.py` et `orchestrator.sh` sont modifiés et non commités. **Le script même qui a rendu le verdict CONFORME est modifié.** Je ne peux pas certifier sa version.

VERDICT KASONGO: **ESCALADE**

Écarts à corriger (Agent 03, après décision du Tech Lead) :
1. Fournir la sortie datée de `./mvnw verify` (0 échec, 0 erreur) sur `fix/sec-003-tenant-isolation@974b36d`.
2. Ajouter des tests d'intégration MockMvc/Testcontainers pour l'intercepteur, dont le scénario « tenant A demande l'ID d'une ressource du tenant B → 404 ». Ou bien faire acter par l'Architecte et le Tech Lead l'écart 403 / 404.
3. Ajouter des tests pour `UserMembershipListener` (rattachement automatique d'un compte créé dans une école).
4. Créer la PR de `fix/sec-003-tenant-isolation` et publier un message `[BE-XXX]` au format de la fiche (endpoints concernés, lien de la PR, transmission aux Agents 04 et 05).
5. Repasser le statut du bus de `DONE` à `IN_PROGRESS` tant que la PR et `mvnw verify` manquent.
6. Dire qui a modifié `orchestrator.sh` (commande `backfill-memberships`) et `ops/`.

Décision humaine requise : **oui**
- Fonctionnalité critique de sécurité : fusion de `fix/sec-003-tenant-isolation`, exécution de la reprise des appartenances sur Neon (base de production), puis activation de `ECOLE_SECURITY_TENANT_MEMBERSHIP_STRICT=true`. Ces trois actions sont réservées au Tech Lead.
- Valider ou refuser la modification de `orchestrator.sh` (gouvernance), et figer la version de `audit/check_handover.py` utilisée pour ce contrôle.
- Changer le secret JWT et purger les jetons en clair de `logs/qa_execution.log`.
- Décider si la dérive contractuelle (14 erreurs, antérieure selon toute vraisemblance) bloque ce ticket ou fait l'objet d'un ticket séparé.
