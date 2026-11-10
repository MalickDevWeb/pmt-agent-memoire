# 📜 Contrat d'Interface API REST — École 221

> **Système** : ERP Multi-Tenant SaaS Éducatif  
> **Auteur (Agent)** : Software Architect  
> **Validé par (Tech Lead)** : ✅ Validé  
> **Base URL** : `/api` (Port standard backend : `8090`)  
> **Format** : JSON (`Content-Type: application/json`)  
> **Statut** : APPROVED  
>
> ⚠️ La section **2.6 Espace Parent** (ajout APP-ARC-06, 2026-11-09) est **IN_REVIEW** : elle attend la Gate 2 du Tech Lead et ne bénéficie pas du statut APPROVED ci-dessus.

---

## 1. Headers Communs Requis

| Header | Type | Requis | Description |
|:---|:---|:---|:---|
| `Authorization` | `String` | Oui (routes protégées) | `Bearer <jwt_token>` délivré lors du login |
| `Content-Type` | `String` | Oui | `application/json` |
| `X-Tenant-Id` | `String` | Conditionnel | Requis si non déduit du token ou du domaine de l'école |

---

## 2. Endpoints Majeurs de la Plateforme

### 2.1 Authentification & Profil (`/api/auth`)

#### `POST /api/auth/login-token`
- **Description** : Authentification et délivrance du jeton d'accès JWT.
- **Codes HTTP** : `200 OK`, `400 Bad Request`, `401 Unauthorized`
- **Request Payload** :
```json
{
  "email": "superadmin@ecole221.sn",
  "password": "<mot_de_passe>"
}
```
- **Response 200 OK** :
```json
{
  "token": "<jwt_token>",
  "id": "user-uuid-101",
  "nom": "Admin",
  "prenom": "Super",
  "email": "superadmin@ecole221.sn",
  "role": { "value": "SUPER_ADMIN" },
  "tenantSlug": "ecole221"
}
```

#### `GET /api/auth/me`
- **Description** : Récupération du profil utilisateur courant à partir du jeton Bearer.
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden`

#### `POST /api/register-school`
- **Description** : Enregistrement et provisionnement autonome d'un nouvel établissement.
- **Codes HTTP** : `201 Created`, `400 Bad Request`, `409 Conflict`

---

### 2.2 Gestion des Utilisateurs & Tenants SuperAdmin (`/api/v1/super-admin`)

#### `GET /api/v1/super-admin/users`
- **Description** : Liste globale paginée des utilisateurs système.
- **Codes HTTP** : `200 OK`, `403 Forbidden`

#### `GET /api/v1/super-admin/tenants`
- **Description** : Liste des établissements enregistrés avec statut d'abonnement.
- **Codes HTTP** : `200 OK`, `403 Forbidden`

---

### 2.3 Gestion Académique & Étudiants (`/api/admin/students`)

#### `GET /api/admin/students`
- **Description** : Récupère la liste des étudiants de l'établissement courant.
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden`
- **Filtres (Query Params)** : `page`, `size`, `search`, `classeId`

#### `POST /api/admin/students`
- **Description** : Inscription d'un nouvel étudiant avec matricule automatique.
- **Codes HTTP** : `201 Created`, `400 Bad Request`, `403 Forbidden`

---

### 2.4 Journalisation & Audit (`/audit`)

#### `GET /audit/logs`
- **Description** : Consultation de la piste d'audit de l'école (actions d'administration).
- **Codes HTTP** : `200 OK`, `403 Forbidden`, `404 Not Found`

---

### 2.5 Référentiels paramétrables (`/api/v1/referentiels`)

Listes de valeurs modifiables sans toucher au code. Valeurs **plateforme** (communes) + **surcharges / ajouts par école**.
Listes disponibles : `expense-category` (OPEN) et `candidate-status` (LOCKED : clés imposées par le code).

#### `GET /api/v1/referentiels`
- **Description** : Liste des référentiels (`ReferentielInfo[]`).
- **Codes HTTP** : `200 OK`, `401 Unauthorized`

#### `GET /api/v1/referentiels/{slug}`
- **Description** : Valeurs effectives pour l'école courante, triées par `sortOrder` (`ReferentielValue[]`).
- **Query Params** : `all` (bool, défaut `false`) — inclut les valeurs masquées.
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `404 Not Found` (slug inconnu)

#### `POST /api/v1/referentiels/{slug}`
- **Description** : Ajoute une valeur propre à l'école (ou plateforme avec `?scope=global`, SUPER_ADMIN). Le `code` est déduit du `label` s'il est absent.
- **Body** : `ReferentielValueInput` (`label` obligatoire).
- **Codes HTTP** : `201 Created`, `400 Bad Request`, `403 Forbidden` (non ADMIN, ou `scope=global` sans SUPER_ADMIN), `409 Conflict` (code existant, liste LOCKED)

#### `PUT /api/v1/referentiels/{slug}/{code}`
- **Description** : Modifie libellé / teinte / ordre / activation. Sur une valeur plateforme, crée une **surcharge** pour l'école.
- **Codes HTTP** : `200 OK`, `400 Bad Request`, `403 Forbidden`, `404 Not Found`, `409 Conflict` (désactiver une valeur système d'une liste LOCKED)

#### `DELETE /api/v1/referentiels/{slug}/{code}`
- **Description** : Supprime une valeur créée par l'école, ou annule une surcharge (retour à la valeur plateforme). Une valeur système se masque (`active=false`), elle ne se supprime pas.
- **Codes HTTP** : `204 No Content`, `403 Forbidden`, `404 Not Found`, `409 Conflict`

> **Impacts** : `POST /api/finance/expenses` attend `category` = code ou libellé d'une catégorie **active** (sinon `400`) et stocke le **code**.
> `PATCH /api/candidatures/candidatures/{id}/statut` normalise (`ACCEPTE`/`VALIDE` → `ACCEPTED`, `REFUSE` → `REJECTED`, `pending` → `EN_ATTENTE`) et renvoie `400` pour une valeur inconnue.

---

### 2.6 Espace Parent (`/api/parent`) — IN_REVIEW (APP-ARC-06)

> **Source de vérité** : `ParentController.java` (`@RequestMapping("/parent")`, l.27) + DTO de `modules/parent/application/port/dto/`. Préfixe `/api` = `server.servlet.context-path` (`application.yaml:4`).
> Ce contrat **décrit l'existant** ; les écarts aux standards (RFC 7807, `201`, pagination) sont listés en fin de section, pas masqués.

**Règles communes à toutes les routes `/api/parent/**`**
- **Rôle requis** : `hasRole("PARENT")` (`SecurityConfig.java:112`). Le contrôleur revérifie le rôle `PARENT` (`ParentController.java:294-302`), sauf `GET /api/parent/professeurs` qui ne repose que sur `SecurityConfig`.
- **Authentification** : cookie HTTP-only ou en-tête `Authorization` Bearer (filtres JWT, APP-SEC-11). L'identifiant du parent est **toujours** celui du compte connecté, jamais un paramètre.
- **`401 Unauthorized`** : aucun compte authentifié (jeton absent/expiré/invalide). Corps produit par `response.sendError(401, "Unauthorized")` (`SecurityConfig.java:117-119`) — pas de Problem Details.
- **`403 Forbidden`** : (a) compte authentifié d'un autre rôle (refus `SecurityConfig`, ou `ResponseStatusException` « Accès refusé: rôle incorrect. Rôle requis: PARENT ») ; (b) sur les 4 routes `/api/parent/enfants/{enfantId}/…` : `enfantId` n'est pas un enfant lié au parent connecté (enfant d'une autre famille) → **corps vide** (`ResponseEntity.status(403).build()`).
- **Dates** : chaînes (`String`), pas de type date ISO garanti sauf mention.
- **Validation** : aucune annotation Bean Validation sur les DTO ; seule `POST /api/parent/messages` valide ses champs.

#### `GET /api/parent/enfants`
- **Description** : Enfants liés au parent connecté (liens `ParentEnfant` enregistrés uniquement, APP-BE-19).
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Response 200 OK** : `ChildDto[]` (liste vide si aucun lien)
```json
[
  { "id": "string", "nom": "string|null", "prenom": "string|null", "matricule": "string|null",
    "filiere": null, "niveau": null, "classe": null, "photoUrl": null }
]
```

#### `GET /api/parent/enfants/{enfantId}/stats`
- **Description** : Tableau de bord d'un enfant. ⚠️ Données fictives (voir « Données non réelles »).
- **Path** : `enfantId` (string).
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle ou enfant d'une autre famille)
- **Response 200 OK** : `ChildStatsDto`
```json
{
  "tauxPresence": 0.0, "nombreAbsences": 0, "nombreRetards": 0, "moyenneGenerale": 0.0,
  "creditValides": 0, "devoirsEnRetard": 0,
  "prochainsExamens": [ { "titre": "string", "date": "string", "salle": "string" } ],
  "coursAujourdhui": [ { "id": "string", "jour": "string", "heure": "string", "cours": "string",
                         "professeur": "string", "salle": "string", "type": "string", "enCours": false } ]
}
```

#### `GET /api/parent/enfants/{enfantId}/presences`
- **Description** : Historique des présences. ⚠️ Données fictives ; le filtre `mois` est accepté mais ignoré.
- **Query Params** : `mois` (optionnel, format `YYYY-MM`).
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle ou enfant d'une autre famille)
- **Response 200 OK** : `PresenceDto[]`
```json
[ { "id": "string", "date": "string", "statut": "PRESENT|ABSENT|RETARD", "cours": "string", "professeur": "string", "heure": "string" } ]
```

#### `GET /api/parent/enfants/{enfantId}/notes`
- **Description** : Notes et résultats académiques. ⚠️ Données fictives.
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle ou enfant d'une autre famille)
- **Response 200 OK** : `GradeDto[]`
```json
[ { "id": "string", "module": "string", "professeur": "string", "cc": 0.0, "examen": 0.0, "moyenne": 0.0,
    "mention": "Excellent|Bien|Assez Bien|Passable|Insuffisant", "ects": 0 } ]
```

#### `GET /api/parent/enfants/{enfantId}/planning`
- **Description** : Emploi du temps hebdomadaire. ⚠️ Données fictives.
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle ou enfant d'une autre famille)
- **Response 200 OK** : `ScheduleDto[]`
```json
[ { "id": "string", "jour": "Lundi", "heure": "08h00 - 10h00", "cours": "string", "professeur": "string",
    "salle": "string", "type": "CM|TD|TP", "enCours": false } ]
```

#### `GET /api/parent/messages`
- **Description** : Boîte de réception du parent. ⚠️ Données fictives.
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Response 200 OK** : `MessageDto[]`
```json
[ { "id": "string", "de": "string", "role": "string", "sujet": "string", "message": "string",
    "date": "2026-11-09", "lu": false, "avatar": null } ]
```

#### `POST /api/parent/messages`
- **Description** : Envoi d'un message à un professeur ou à l'administration. ⚠️ Non persisté (voir note).
- **Codes HTTP** : `200 OK`, `400 Bad Request` (champ manquant ou vide), `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Request Payload** : `SendMessageRequestDto` (les 3 champs obligatoires et non vides)
```json
{ "destinataireId": "string", "sujet": "string", "message": "string" }
```
- **Response 200 OK** :
```json
{ "success": true, "message": { "...": "MessageDto" } }
```
- **Response 400** : `{ "error": "Tous les champs sont obligatoires" }`

#### `PATCH /api/parent/messages/{messageId}/lu`
- **Description** : Marque un message comme lu. ⚠️ Sans effet en base (voir note).
- **Request Payload** : aucun.
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Response 200 OK** : `{ "success": true }`

#### `GET /api/parent/candidatures`
- **Description** : Dossiers d'inscription soumis par le parent. ⚠️ Données fictives.
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Response 200 OK** : `ApplicationDto[]`
```json
[ { "id": "string", "enfant": "string", "filiere": "string", "niveau": "string", "dateDepot": "string",
    "statut": "EN_ATTENTE|ACCEPTE|REFUSE", "progress": 0, "etape": "string", "commentaire": null } ]
```

#### `POST /api/parent/inscrire-enfant`
- **Description** : Soumission d'un dossier de candidature pour un enfant. ⚠️ Non persisté (voir note).
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Request Payload** : `EnrollChildPayloadDto` (aucun champ validé côté serveur)
```json
{ "prenom": "string", "nom": "string", "dateNaissance": "string", "lieuNaissance": "string", "nationalite": "string",
  "sexe": "string", "email": "string", "telephone": "string", "filiere": "string", "niveau": "string",
  "diplomePrecedent": "string", "etablissementPrecedent": "string" }
```
- **Response 200 OK** : `{ "success": true, "dossierId": "d-xxxxxxxx" }`

#### `GET /api/parent/paiements`
- **Description** : Scolarité et échéances de paiement. Aucune source réelle n'est branchée : le backend renvoie une réponse **vide explicitement marquée** `statut: "non_disponible"` et **jamais** de transaction fictive (APP-BE-18, backend 2f34e62 ; `PaymentDto.java:16-22`, `ParentService.java:258-261`).
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Response 200 OK** : `PaymentDto`
```json
{
  "totalAnnuel": 0,
  "echeances": [],
  "statut": "non_disponible"
}
```
- **Champ `statut`** : `"disponible"` (données issues d'une source réelle) | `"non_disponible"` (aucune source ; `totalAnnuel = 0`, `echeances = []`). Valeur actuelle : toujours `"non_disponible"`.
- **Échéance** (`echeances[]`, lorsque `statut = "disponible"`) : `{ "id": "string", "label": "string", "montant": 0, "echeance": "string", "statut": "PAYE|EN_COURS|RETARD", "datePaiement": "string" }` — `totalAnnuel` et `montant` sont des entiers (`long`).

#### `PATCH /api/parent/profil`
- **Description** : Mise à jour du profil parent. ⚠️ Non persisté : le corps reçu est renvoyé tel quel.
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Request Payload / Response 200 OK** : `ParentProfileDto`
```json
{ "email": "string", "telephone": "string", "adresse": "string", "profession": "string" }
```

#### `POST /api/parent/rdv`
- **Description** : Demande de rendez-vous avec un professeur (persisté via `AppointmentRepositoryPort.save`).
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Request Payload** : `AppointmentRequestDto`
```json
{ "professeurId": "string", "dateSouhaitee": "string", "motif": "string" }
```
- **Response 200 OK** : `{ "success": true, "rdvId": "string" }`

#### `GET /api/parent/rdv`
- **Description** : Rendez-vous et visioconférences du parent. ⚠️ Voir note (repli sur tous les RDV + RDV d'amorçage).
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Response 200 OK** : tableau d'objets
```json
[ { "id": "string", "parentId": "string", "professeurId": "string", "professeurNom": "string",
    "dateSouhaitee": "string", "motif": "string", "status": "string", "meetUrl": "string|null", "createdAt": "string (vide si absent)" } ]
```

#### `GET /api/parent/professeurs`
- **Description** : Professeurs proposés pour la prise de rendez-vous (comptes de rôle `PROFESSEUR`).
- **Codes HTTP** : `200 OK`, `401 Unauthorized`, `403 Forbidden` (autre rôle, via `SecurityConfig` uniquement)
- **Response 200 OK** :
```json
[ { "id": "string", "nom": "string", "prenom": "string", "email": "string", "displayName": "string" } ]
```

#### `POST /api/parent/presences/{presenceId}/justifier`
- **Description** : Justification d'une absence/retard. ⚠️ Non persisté (voir note).
- **Query Params** (pas de corps JSON) : `motif` (**obligatoire**), `fileUrl` (optionnel).
- **Codes HTTP** : `200 OK`, `400 Bad Request` (`motif` absent — rejet Spring, format du corps non vérifié), `401 Unauthorized`, `403 Forbidden` (autre rôle)
- **Response 200 OK** : `{ "success": true, "justificatifId": "justif-xxxxxxxx" }`

#### ⚠️ Données non réelles (carte APP-BE-19)

Constat au 2026-11-09 sur `ParentService.java` (lignes citées). Le Frontend **ne doit pas** présenter ces données comme réelles.

| Route | Méthode du service | État constaté |
|:---|:---|:---|
| `GET /api/parent/enfants/{enfantId}/stats` | `getChildStats` (l.73-108) | **Fictif** : valeurs codées en dur (87 %, 14.5, examens « Algorithmique Avancée »…) |
| `GET /api/parent/enfants/{enfantId}/presences` | `getChildPresences` (l.110-123) | **Fictif** : 3 présences fixes, `mois` ignoré |
| `GET /api/parent/enfants/{enfantId}/notes` | `getChildGrades` (l.125-136) | **Fictif** : 2 notes fixes |
| `GET /api/parent/enfants/{enfantId}/planning` | `getChildSchedule` (l.138-150) | **Fictif** : 4 créneaux fixes |
| `GET /api/parent/messages` | `getParentMessages` (l.152-180) | **Fictif** : 2 messages fixes |
| `GET /api/parent/candidatures` | `getParentApplications` (l.220-239) | **Fictif** : 1 dossier fixe « Aminata Diallo » |
| `GET /api/parent/enfants` | `getEnfantsByParentId` (l.50-71) | **Réel mais incomplet** (corrigé APP-BE-19) : liens réels ; `nom`/`prenom`/`matricule` du compte (ou `null`), `filiere`/`niveau`/`classe`/`photoUrl` toujours `null` |
| `POST /api/parent/messages` | `sendMessage` (l.182-200) | **Non persisté** : renvoie un `MessageDto` simulé |
| `PATCH /api/parent/messages/{messageId}/lu` | `markMessageAsRead` (l.202-218) | **Sans effet** |
| `POST /api/parent/inscrire-enfant` | `enrollChild` (l.241-251) | **Non persisté** : `dossierId` généré, rien n'est enregistré |
| `PATCH /api/parent/profil` | `updateParentProfile` (l.264-271) | **Non persisté** : écho du corps |
| `POST /api/parent/presences/{presenceId}/justifier` | `justifyAbsence` (l.329-337) | **Non persisté** : identifiant généré |
| `GET /api/parent/rdv` | `getParentAppointments` (l.294-327) | **Partiellement fictif** : si le parent n'a aucun RDV, repli sur `findAll()` puis création d'un RDV d'amorçage « Dr. Sall » |
| `POST /api/parent/rdv` | `requestAppointment` (l.273-292) | Persisté ; `professeurNom` vaut « Dr. Sall (Algorithmique & IA) » si `professeurId` ne contient pas « — » |
| `GET /api/parent/professeurs` | contrôleur (l.247-266) | Réel ; **2 professeurs fictifs** renvoyés si aucun compte `PROFESSEUR` |
| `GET /api/parent/paiements` | `getParentPayments` (l.253-262) | **Honnête** : `statut: "non_disponible"`, aucune donnée fictive |

#### Écarts aux standards du contrat (constat, sans modification du code)
- Erreurs **non conformes RFC 7807** : `401` (`sendError`), `403` filiation (corps vide), `400` messages (`{ "error": … }`).
- Créations en **`200 OK`** et non `201 Created` + `Location` : les 4 routes POST de cette section (envoi de message, inscription d'enfant, demande de RDV, justification d'absence).
- Pas de pagination, pas de `version` (optimistic locking), pas de `X-Idempotency-Key`.
- Pas de `404 Not Found` : un `messageId` / `presenceId` inexistant renvoie `200`.

---

## 3. Interfaces & Modèles TypeScript Exportables

```typescript
export type ReferentielSlug = 'expense-category' | 'candidate-status';
export type ReferentielScope = 'GLOBAL' | 'SURCHARGE' | 'ECOLE';

export interface ReferentielInfo { slug: ReferentielSlug; label: string; mode: 'OPEN' | 'LOCKED'; }

export interface ReferentielValue {
  code: string;            // clé stable stockée en base (ex. MATERIEL)
  label: string;           // libellé affiché, modifiable
  color: string | null;    // teinte : slate | amber | emerald | red | sky | violet | indigo
  sortOrder: number;
  active: boolean;
  system: boolean;         // valeur de départ de la plateforme
  locked: boolean;         // liste dont les clés sont imposées par le code
  scope: ReferentielScope;
}

export interface ReferentielValueInput { code?: string; label?: string; color?: string; sortOrder?: number; active?: boolean; }
```

```typescript
export interface User {
  id: string;
  nom: string;
  prenom: string;
  email: string;
  role: { value: string };
  tenantSlug?: string;
  telephone?: string;
}

export interface AuthResponse {
  token: string;
  id: string;
  nom: string;
  prenom: string;
  email: string;
  role: { value: string };
  tenantSlug?: string;
}

export interface Student {
  id: string;
  organizationId: string;
  matricule: string;
  nom: string;
  prenom: string;
  email?: string;
  classeId?: string;
  telephone?: string;
  dateNaissance?: string;
}

export interface Tenant {
  id: string;
  nom: string;
  slug: string;
  domaine?: string;
  statut: 'ACTIF' | 'SUSPENDU' | 'PERIODE_ESSAI';
  createdAt: string;
}

export interface AuditLog {
  id: string;
  organizationId: string;
  actionType: string;
  entityType: string;
  actorId: string;
  actorName: string;
  severity: 'info' | 'warning' | 'critical';
  status: 'success' | 'failure';
  actionTimestamp: string;
}
```

```typescript
// Espace Parent (/api/parent) — IN_REVIEW (APP-ARC-06). Les String Java sans validation peuvent être null.
export interface ChildDto {
  id: string;
  nom: string | null; prenom: string | null; matricule: string | null;
  filiere: string | null; niveau: string | null; classe: string | null; photoUrl: string | null;
}

export interface ExamDto { titre: string; date: string; salle: string; }
export interface CourseDto {
  id: string; jour: string; heure: string; cours: string; professeur: string; salle: string; type: string; enCours: boolean;
}
export interface ChildStatsDto {
  tauxPresence: number; nombreAbsences: number; nombreRetards: number; moyenneGenerale: number;
  creditValides: number; devoirsEnRetard: number;
  prochainsExamens: ExamDto[]; coursAujourdhui: CourseDto[];
}

export interface PresenceDto {
  id: string; date: string; statut: 'PRESENT' | 'ABSENT' | 'RETARD'; cours: string; professeur: string; heure: string;
}

export interface GradeDto {
  id: string; module: string; professeur: string; cc: number; examen: number; moyenne: number;
  mention: 'Excellent' | 'Bien' | 'Assez Bien' | 'Passable' | 'Insuffisant'; ects: number;
}

export interface ScheduleDto {
  id: string; jour: string; heure: string; cours: string; professeur: string; salle: string;
  type: 'CM' | 'TD' | 'TP'; enCours: boolean;
}

export interface MessageDto {
  id: string; de: string; role: string; sujet: string; message: string; date: string; lu: boolean; avatar: string | null;
}
export interface SendMessageRequestDto { destinataireId: string; sujet: string; message: string; }
export interface SendMessageResponse { success: true; message: MessageDto; }

export interface ApplicationDto {
  id: string; enfant: string; filiere: string; niveau: string; dateDepot: string;
  statut: 'EN_ATTENTE' | 'ACCEPTE' | 'REFUSE'; progress: number; etape: string; commentaire: string | null;
}
export interface EnrollChildPayloadDto {
  prenom: string; nom: string; dateNaissance: string; lieuNaissance: string; nationalite: string; sexe: string;
  email: string; telephone: string; filiere: string; niveau: string; diplomePrecedent: string; etablissementPrecedent: string;
}

export type PaymentStatut = 'disponible' | 'non_disponible';
export interface PaymentInstallmentDto {
  id: string; label: string; montant: number; echeance: string;
  statut: 'PAYE' | 'EN_COURS' | 'RETARD'; datePaiement: string | null;
}
export interface PaymentDto { totalAnnuel: number; echeances: PaymentInstallmentDto[]; statut: PaymentStatut; }

export interface ParentProfileDto { email: string; telephone: string; adresse: string; profession: string; }

export interface AppointmentRequestDto { professeurId: string; dateSouhaitee: string; motif: string; }
export interface ParentAppointment {
  id: string; parentId: string; professeurId: string; professeurNom: string; dateSouhaitee: string;
  motif: string; status: string; meetUrl: string | null; createdAt: string;
}
export interface ParentProfesseur { id: string; nom: string; prenom: string; email: string; displayName: string; }
```
