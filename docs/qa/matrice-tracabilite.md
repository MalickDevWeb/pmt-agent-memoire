# Matrice de traçabilité Exigences ↔ Tests QA (APP-QA-01)

- **Rédigée le** : 2026-11-09 vers 13:00 (Dakar), par Aïssatou Ba, QA Engineer (Agent 05)
- **Source d'exécution** : `logs/qa_execution.log`, en-tête « Exécution des tests QA certifiée : 2026-11-09 12:39:48 » (l.1). Bilan : 16 modules sur 16 PASSED, `QA_RESULT: PASS` (l.682-685).
- **Référentiel** : `docs/requirements.md` (US-01 à US-03, BR-01 à BR-05) et `docs/requirements/FEAT-001-auth-onboarding.md` (FEAT-001-US-01/02, SC-01 à SC-04, BR-01 à BR-05, NFR).
- **Méthode** :
  1. J'ai relu les commentaires `# Exigence :` des scripts `test_auth_module.sh` (l.11, 59, 86) et `test_tenant_isolation_module.sh` (l.20, 25, 30, 35, 39).
  2. J'ai comparé chaque étape au texte exact de l'exigence.
  3. J'ai relevé le statut dans le log.
- **Comment lire le log** : `lib_http_assert.sh` intercepte chaque appel `curl`.
  - Par défaut, il accepte un statut 2xx ou 3xx (l.9, 38-39). Avec `EXPECT_STATUS`, il exige ce code exact.
  - Le compteur « N / N » ne compte que les requêtes (l.36, 85). Les échecs `assert_json_*` sont journalisés à part (l.52, 65, 76) et feraient afficher ❌.
  - Le log ne donne donc **pas** de statut par assertion. Un PASS ci-dessous signifie : le module affiche « N / N … conformes » et aucune anomalie n'est listée.
- **Aucune exécution nouvelle** pour cette matrice. Je n'ai pas lancé `qa-tests`.

> ⚠️ **Écart entre le script et le log (fait)** : la version actuelle de `test_auth_module.sh` contient `EXPECT_STATUS=201` sur `POST /register-school` (l.75), et le commentaire l.59 indique « 201 asserté (EXPECT_STATUS) ».
> Cette assertion **n'existait pas** lors de l'exécution de 12:39:48. Preuve : le log montre `Status: 200` (l.41) puis « 9 / 9 … conformes » (l.51). Avec `EXPECT_STATUS=201`, la lib aurait journalisé une anomalie (lib l.38-40).
> Au début de la présente session, le commentaire l.59 disait encore « couverture partielle (201 et statut PENDING non assertés) ». Il a changé pendant la session, **sans écriture de ma part**. L'auteur m'est inconnu (`git-status` : `M test_auth_module.sh`).
> Cette matrice décrit **l'état exécuté à 12:39:48**.

## 1. Matrice

| # | Exigence (id + intitulé exact) | Script | Étape | Assertion vérifiée (à 12:39:48) | Statut (log) |
|---|---|---|---|---|---|
| 1 | US-01 « Scénario: Authentification réussie » / FEAT-001-SC-01 « Connexion réussie avec identifiants valides » | test_auth_module.sh | 1️⃣ POST /auth/login-token (l.12-29) | Code HTTP 2xx (lib) et `-eq 200` (l.23). **Non asserté** : token, rôle et tenantSlug dans le JSON (ils figurent bien dans la réponse, log l.15, mais aucun test ne les vérifie) ; entrée d'audit de succès. | PASS (l.14, l.51), **couverture partielle** |
| 2 | US-01 « Scénario: Échec de connexion (Identifiants incorrects) » / FEAT-001-SC-02 « Rejet en cas d'identifiants erronés » | test_auth_module.sh | 🔒 [SEC-002], 4 requêtes (l.88-93) | `EXPECT_STATUS=401` × 4 : 2 mauvais mots de passe pour un compte existant, 2 essais sur un email inconnu. Le code est le même (401) que l'email existe ou non. Le corps n'est pas comparé (`-o /dev/null`). **Non asserté** : IP, tentative et User-Agent consignés dans le journal de sécurité. | PASS (l.45, l.51), **couverture partielle** |
| 3 | US-02 « Scénario: Création nominale d'un établissement » / FEAT-001-SC-03 « Enregistrement nominal d'une école » | test_auth_module.sh | 5️⃣ POST /register-school (l.60-83) | À 12:39:48 : code 2xx/3xx seulement (défaut de la lib). **Non asserté** : 201 Created (exigé par US-02), statut initial PENDING, création du compte administrateur. | PASS (l.41, l.51), **couverture partielle**. Le 201 n'est pas respecté, voir OBS-01 |
| 4 | BR-01 « Isolation Multi-Tenant » (préparation) | test_tenant_isolation_module.sh | 1️⃣ Le tenant A crée une dépense témoin (l.21-23) | Code 2xx (défaut). C'est une étape de préparation, pas une vérification de la règle. | PASS (l.669, l.676) |
| 5 | BR-01 « Isolation Multi-Tenant » (lecture) | test_tenant_isolation_module.sh | 2️⃣ GET /finance/expenses par le tenant B sur sa propre école (l.26-28) | Code 2xx et `assert_json_array_empty` : aucune dépense portant le marqueur de A. Test indirect (effet observable). Ne couvre **pas** US-03 (`/admin/students`). | PASS (l.670, l.676) |
| 6 | BR-01 / FEAT-001-BR-01 « Isolation Multi-Tenant » (en-tête falsifié) | test_tenant_isolation_module.sh | 3️⃣ Le tenant B envoie `X-Tenant-Slug: ecole-221`, puis `X-Tenant-ID: default-tenant-id` (l.31-33) | `EXPECT_STATUS=403` × 2 | PASS (l.671, l.676) |
| 7 | BR-01 / FEAT-001-BR-01 « Isolation Multi-Tenant » (sans en-tête) | test_tenant_isolation_module.sh | 4️⃣ Le tenant B n'envoie aucun en-tête de tenant (l.36-37) | `EXPECT_STATUS=403` | PASS (l.672, l.676) |
| 8 | BR-01 / FEAT-001-BR-01 « Isolation Multi-Tenant » (écriture) | test_tenant_isolation_module.sh | 5️⃣ Le tenant B fait un POST dans le référentiel de A, puis A relit (l.40-45) | `EXPECT_STATUS=403` sur le POST, code 2xx sur la relecture, et `assert_json_array_empty` : le code créé par B est absent chez A | PASS (l.673, l.676) |

**Volume rattaché** : 9 requêtes dans `test_tenant_isolation_module.sh` (log l.676), dont 2 logins sans exigence propre. Dans `test_auth_module.sh`, 6 requêtes sur 9 sont rattachées (étapes 1 et 5, plus les 4 × 401). Les 3 autres (/auth/me, /auth/login avec cookie, /auth/logout) n'ont aucune exigence (§3). J'ai aussi 2 assertions JSON, toutes deux dans le script d'isolation.

**Remarque sur les codes attendus (fait)** : BR-01 et FEAT-001-BR-01 ne fixent aucun code HTTP. Les `EXPECT_STATUS=403` des étapes 3 à 5 ne viennent donc pas d'un texte d'exigence. La fiche QA, de son côté, demande un 404 pour l'accès par ID à une ressource d'un autre tenant. Ici, l'accès porte sur un listing via un en-tête falsifié : la situation n'est pas la même. Je ne tranche pas, c'est à confirmer par l'Architecte ou le Product Analyst.

## 2. Exigences sans test

| Exigence | Intitulé | Constat |
|---|---|---|
| US-03 | Isolation Multi-Tenant des Données Étudiants, « Scénario: Filtrage strict par organization_id » | Aucun script ne compare `GET /api/admin/students` entre deux tenants. |
| BR-02 | Unicité du Matricule | Aucun test de doublon de matricule. |
| BR-03 | Sécurité des Mots de Passe (BCrypt, coût ≥ 12) | Non vérifiable en boîte noire. Relève de la revue de code ou d'un test boîte blanche. |
| BR-04 | Intégrité des Évaluations (note entre 0 et 20, figée après clôture) | Aucun test de borne ni de clôture. |
| BR-05 | Audit Trail | Aucun test ne vérifie `audit_logs`. |
| FEAT-001-SC-04 | Rejet si le slug de l'école existe déjà | Aucun second POST /register-school avec le même slug. |
| FEAT-001-BR-02 | Unicité du Slug | Même constat que SC-04. |
| FEAT-001-BR-03 | Chiffrement Mots de Passe | Même constat que BR-03. |
| FEAT-001-BR-04 | Activation SuperAdmin (reste `PENDING`) | Le statut PENDING n'est pas asserté. Il est seulement visible dans le log (l.42). |
| FEAT-001-BR-05 | Audit Connexions | Non testé. |
| FEAT-001 NFR | JWT < 250 ms ; durée de vie 24 h et HMAC-SHA384 ; volumétrie ; audit IP, identifiant et User-Agent | Non testé. Aucune mesure de latence dans les scripts. |

Les fichiers de FEAT-002 à FEAT-005 sont marqués `APPROVED` dans `docs/requirements.md` (l.109-112) mais sont absents de `docs/requirements/` : seul `FEAT-001-auth-onboarding.md` est présent. Leurs exigences ne peuvent donc pas être tracées.

## 3. Tests sans exigence

Le log contient **16 modules** (l.682), et le dossier racine compte 16 scripts `test_*.sh`. Hors des 2 scripts tracés, il en reste donc **14, et non 12** comme l'indiquait la consigne. Mon message [APP-QA-01] omettait `test_superadmin_tenants.sh` et `test_final_modules.sh`.

| Script | Statut (log) | Remarque |
|---|---|---|
| test_superadmin_tenants.sh | PASS, 8/8 (l.95-96) | Aucune exigence du référentiel |
| test_billing_module.sh | PASS, 5/5 (l.113-114) | Idem |
| test_admin_module.sh | PASS, 6/6 (l.150-151) | Idem (US-03 non testée ici) |
| test_professor_module.sh | PASS, 6/6 (l.188-189) | Pourrait relever de BR-04, mais aucune assertion de borne (voir OBS-02) |
| test_student_module.sh | PASS, 6/6 (l.225-226) | Aucune exigence |
| test_parent_module.sh | PASS, 10/10 (l.270-271) | Idem |
| test_security_module.sh | PASS, 7/7 (l.311-312) | Idem (FEAT-005 absente) |
| test_finance_module.sh | PASS, 7/7 (l.353-354) | Idem |
| test_planning_module.sh | PASS, 9/9 (l.394-395) | Idem (FEAT-004 absente) |
| test_candidatures_module.sh | PASS, 17/17 (l.513-514) | Idem |
| test_collaboration_module.sh | PASS, 8/8 (l.559-560) | Idem |
| test_dashboard_module.sh | PASS, 6/6 (l.596-597) | Idem |
| test_final_modules.sh | PASS, 10/10 (l.641-642) | Idem |
| test_referentiels_module.sh | PASS, 28/28 (l.663-664) | Idem |

S'y ajoutent, dans `test_auth_module.sh`, les étapes 2️⃣ GET /auth/me, 3️⃣ POST /auth/login (cookie) et 4️⃣ POST /auth/logout. Elles sont dans le périmètre de FEAT-001 (l.22-24) mais aucun scénario ne leur correspond.

**Constat (fait)** : une recherche de `assert_json_` dans le dépôt montre que seul `test_tenant_isolation_module.sh` appelle les fonctions d'assertion JSON de la lib (l.28 et l.45). Ce constat ne dit rien d'éventuels contrôles écrits à la main (`if`, `jq`) dans les autres scripts : je ne les ai pas audités ici.

**Référentiel** : aucun identifiant `SCN-xxx` n'existe. FEAT-001 utilise la forme `FEAT-001-SC-xx`, alors que la fiche QA impose de citer `[SCN-xxx]`.

## 4. Observations

- **OBS-01 (FAIT, sévérité MAJOR)** : `POST /api/register-school` renvoie **200** au lieu du **201 Created** exigé par US-02 (requirements.md l.74). Preuve : log l.41 `Status: 200`.
  - À 12:39:48, le test passait parce qu'il n'exigeait qu'un 2xx (l.51).
  - Le corps de la réponse (l.42) contient à la fois `"pending":false` et `"status":{"value":"PENDING"}`. Je constate l'incohérence apparente sans la qualifier.
  - Avec l'`EXPECT_STATUS=201` ajouté depuis (voir l'encadré ⚠️), la prochaine exécution devrait échouer tant que le backend renvoie 200. C'est une **prévision**, pas encore une preuve.
  - Reproduction : `curl -s -w '%{http_code}' -X POST http://localhost:8090/api/register-school -H 'Content-Type: application/json' -d '{"schoolName":"…","slug":"lycee-test-XXXX","adminEmail":"…","adminFirstName":"…","adminLastName":"…"}'`.
  - Destinataire : Backend.
- **OBS-02 (HYPOTHÈSE, à qualifier)** : le test envoie `{"noteCc": 16.5, "noteExam": 15.0}` (test_professor_module.sh l.56), mais la réponse contient `"cc":0.0,"examen":0.0,"finalGrade":0.0,"mention":"F"` (log l.174).
  - Hypothèse : les notes envoyées sont ignorées, peut-être à cause d'un nom de champ différent de celui que le DTO attend. Je ne l'ai pas vérifié dans le contrat d'API.
  - Destinataire : Backend, une fois l'hypothèse qualifiée.
- **OBS-03 (HYPOTHÈSE, à qualifier)** : `GET /admin/students/{id}/profile360` renvoie le matricule `"MAT-2023-usr-9cf63f50"` (log l.144), alors que l'étudiant vient d'être créé avec le matricule `"2026-ET-1900"` (log l.136).
  - Les autres champs de la réponse (bacMention, lycée, dates 2023, connectionLogs) semblent statiques.
  - Hypothèse : données en dur ou de démonstration, et non lues en base.
  - Écart de contrat déjà signalé sur le bus (agent_messages.md l.471) : `profile360` est absent de `docs/api-contract.md`.
