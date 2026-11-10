# 🗄️ Modélisation Base de Données — École 221

> **SGBD Cible** : PostgreSQL 15+  
> **Auteur (Agent)** : Database Architect  
> **Validé par (Tech Lead)** : ✅ Validé  
> **Stratégie Multi-Tenant** : Schema partagé avec colonne discriminante (`organization_id`)  
> **Statut** : APPROVED  

---

## 1. Schéma Relationnel & Tables Clés

### 1.1 Tables Globales (Plateforme SaaS & IAM Global)
Ces tables hébergent la gestion globale et ne sont pas cloisonnées par un tenant :

| Table | Clé Primaire | Description |
|:---|:---|:---|
| `organizations` | `id` (VARCHAR) | Définition des établissements abonnés (nom, slug, domaine, statut) |
| `users` | `id` (VARCHAR) | Identités globales, credentials (BCrypt) et rôle (`SUPER_ADMIN`, `ADMIN`, etc.) |
| `plans` | `id` (VARCHAR) | Grille tarifaire (Basic, Pro, Enterprise, limites d'étudiants) |
| `subscriptions` | `id` (VARCHAR) | Abonnements actifs des écoles avec date d'échéance et statut de paiement |

---

### 1.2 Tables Cloisonnées par Établissement (`organization_id`)
Toutes ces tables intègrent obligatoirement `organization_id` avec annotation Hibernate `@TenantId` :

| Table | Clé Primaire | Colonne Tenant | Description |
|:---|:---|:---|:---|
| `students` | `id` (VARCHAR) | `organization_id` | Dossiers étudiants (matricule, nom, prénom, classe, tuteur) |
| `professors` | `id` (VARCHAR) | `organization_id` | Enseignants, spécialités, statut et contact |
| `classes` | `id` (VARCHAR) | `organization_id` | Classes académiques (ex: Terminale S2, Licence 1 Informatique) |
| `filieres` | `id` (VARCHAR) | `organization_id` | Filières d'études (Sciences, Gestion, Technologies) |
| `courses` | `id` (VARCHAR) | `organization_id` | Matières et unités d'enseignement |
| `grades` | `id` (VARCHAR) | `organization_id` | Évaluations, coefficients et notes (/20) |
| `rooms` | `id` (VARCHAR) | `organization_id` | Salles de cours, laboratoires et capacités |
| `slots` | `id` (VARCHAR) | `organization_id` | Séances et créneaux d'emploi du temps |
| `audit_logs` | `id` (VARCHAR) | `organization_id` | Journal des actions administratives et modifications |
| `security_events`| `id` (VARCHAR) | `organization_id` | Événements de contrôle aux portiques et scans de badges |

---

## 2. Contraintes d'Unicité & Index de Performance

```sql
-- 1. Unicité du matricule par établissement
ALTER TABLE students 
ADD CONSTRAINT uq_students_org_matricule UNIQUE (organization_id, matricule);

-- 2. Index composites pour l'accélération des requêtes multi-tenant
CREATE INDEX idx_students_org_classe ON students (organization_id, classe_id);
CREATE INDEX idx_grades_org_student ON grades (organization_id, student_id);
CREATE INDEX idx_slots_org_room_time ON slots (organization_id, room_id, start_time, end_time);
CREATE INDEX idx_audit_org_timestamp ON audit_logs (organization_id, action_timestamp DESC);
CREATE INDEX idx_security_org_timestamp ON security_events (organization_id, event_timestamp DESC);
```

---

## 3. Script DDL de Migration Type

```sql
-- Création type d'une table avec isolation stricte
CREATE TABLE IF NOT EXISTS students (
    id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    matricule VARCHAR(30) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    telephone VARCHAR(30),
    classe_id VARCHAR(64),
    date_naissance DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uq_students_matricule_per_org UNIQUE (organization_id, matricule)
);
```

---

## 4. Référentiels paramétrables — table `reference_values`

Remplace les listes écrites en dur dans le code (catégories, statuts…). Flyway étant désactivé
(`ddl-auto: update`), la table est créée par Hibernate et remplie par `ReferenceDataSeeder` (idempotent).

```sql
CREATE TABLE IF NOT EXISTS reference_values (
    id              VARCHAR(255) PRIMARY KEY,
    list_code       VARCHAR(40)  NOT NULL,          -- EXPENSE_CATEGORY, CANDIDATE_STATUS
    code            VARCHAR(40)  NOT NULL,          -- clé stable stockée dans les tables métier
    label           VARCHAR(80)  NOT NULL,          -- libellé affiché (modifiable)
    color           VARCHAR(20),                    -- teinte (slate, amber, emerald…)
    sort_order      INTEGER      NOT NULL,
    active          BOOLEAN      NOT NULL,          -- false = masquée (plus proposée à la saisie)
    system_value    BOOLEAN      NOT NULL,          -- valeur de départ de la plateforme
    organization_id VARCHAR(255),                   -- NULL = valeur plateforme ; sinon école
    updated_at      TIMESTAMP    NOT NULL,
    CONSTRAINT uk_reference_value_scope UNIQUE (list_code, code, organization_id)
);
CREATE INDEX idx_reference_values_list_org ON reference_values (list_code, organization_id);
```

**Isolation multi-tenant** : pas de `@TenantId` (les lignes `organization_id IS NULL` sont partagées) ;
toutes les lectures filtrent `organization_id IS NULL OR organization_id = :tenant`. Une ligne école portant
le même `code` qu'une ligne plateforme est une **surcharge** (elle la remplace pour cette école).

**Données normalisées au démarrage** (`LegacyReferenceDataNormalizer`) :
`expenses.category` (« Matériel » → `MATERIEL`…) et `candidates.admission_status` (« pending », « ACCEPTE »… → clé `CandidateStatus`).
