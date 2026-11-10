# 📋 Spécifications Fonctionnelles & Métier — École 221 ERP Multi-Tenant

> **Plateforme** : École 221 (Système Global de Gestion Académique, Administrative & Sécurité)  
> **Auteur (Agent)** : Product Analyst  
> **Validé par (Tech Lead)** : ✅ Validé  
> **Date de référence** : 2026-11-05  
> **Statut** : APPROVED  

---

## 1. Contexte & Problématique Métier

École 221 est une plateforme SaaS éducative multi-tenant conçue pour administrer des établissements d'enseignement supérieur et secondaire en Afrique de l'Ouest.
Elle gère l'isolation stricte des données entre écoles partenaires tout en fournissant une interface fluide et unifiée pour l'ensemble des acteurs de la communauté éducative.

- **Acteurs Cibles** :
  - **SuperAdmin** : Gestionnaire global de la plateforme, gestion des souscriptions, plans et création des établissements (Tenants).
  - **Admin Établissement** : Gestionnaire de l'école (inscriptions, filières, classes, plannings, finances, personnel).
  - **Professeur** : Saisie des cours, devoirs, examens, notes et validation des présences.
  - **Étudiant** : Consultation des notes, planning des cours, téléchargement de supports pédagogiques, badge QR d'accès.
  - **Parent** : Suivi des notes, absences, paiements de scolarité et communication avec l'administration.
  - **Vigil / Sécurité** : Contrôle d'accès physique par scanneur de badges QR code synchronisé en temps réel.

---

## 2. Périmètre (Scope)

### ✅ Dans le périmètre (In-Scope)
1. **Multi-Tenancy SaaS Strict** : Partitionnement logique des données par établissement (`organization_id`).
2. **Authentification Unifiée & RBAC** : Login par token JWT et session cookie, support SuperAdmin global et utilisateurs d'établissement.
3. **Gestion Académique & Pédagogique** : Étudiants, professeurs, promotions, filières, classes, devoirs, évaluations et bulletins.
4. **Planification & Emplois du Temps** : Réservation de salles, gestion des conflits d'horaires et créneaux.
5. **Gestion Financière** : Échéanciers de scolarité, paiements, dépenses et facturation.
6. **Contrôle d'Accès & Sécurité Campus** : Badge QR étudiant dynamique et journalisation des événements de sécurité.
7. **Espace Collaboratif Temps Réel** : Messagerie STOMP/WebSocket et partage de documents.

### ❌ Hors périmètre (Out-of-Scope)
- Paiement par cryptomonnaie (seuls les moyens usuels : Wave, Orange Money, Carte, Virement sont ciblés).
- Reconnaissance faciale biométrique (remplacée par le scan sécurisé de QR codes signés).

---

## 3. User Stories & Critères d'Acceptation (Format Gherkin)

### US-01 : Authentification & Délivrance du Token JWT
> **En tant qu'** utilisateur de la plateforme (SuperAdmin ou membre d'un établissement)  
> **Je veux** m'authentifier avec mon email et mon mot de passe  
> **Afin d'** accéder aux ressources et API autorisées selon mon rôle  

```gherkin
Scénario: Authentification réussie
  Étant donné que l'utilisateur fournit un email valide et son mot de passe
  Quand la requête POST /api/auth/login-token est soumise
  Alors le système retourne un code HTTP 200 OK
  Et le payload JSON contient le token JWT, le rôle et le tenantSlug

Scénario: Échec de connexion (Identifiants incorrects)
  Étant donné que l'utilisateur saisit un mot de passe erroné
  Quand la requête POST /api/auth/login-token est envoyée
  Alors le système rejette avec un code HTTP 401 Unauthorized
```

### US-02 : Enregistrement d'un Nouvel Établissement (Onboarding)
> **En tant que** responsable d'école  
> **Je veux** inscrire mon établissement sur la plateforme  
> **Afin de** démarrer la gestion de mon école de manière autonome  

```gherkin
Scénario: Création nominale d'un établissement
  Étant donné un nom d'école, un slug unique et l'email de l'administrateur
  Quand la requête POST /api/register-school est soumise
  Alors le système crée l'organisation avec son organization_id dédié
  Et initialise le compte administrateur associé
  Et retourne un code HTTP 201 Created
```

### US-03 : Isolation Multi-Tenant des Données Étudiants
> **En tant qu'** administrateur de l'école A  
> **Je veux** lister et gérer uniquement les étudiants de mon établissement  
> **Afin de** préserver la confidentialité et la séparation des données  

```gherkin
Scénario: Filtrage strict par organization_id
  Étant donné un token JWT associé à l'organisation "ecole-alpha"
  Quand l'administrateur appelle GET /api/admin/students
  Alors le système filtre automatiquement les résultats par le tenantId courant
  Et aucun étudiant d'un autre établissement n'apparaît dans la réponse
```

---

## 4. Matrice des Règles Métier (Business Rules)

| Réf | Règle | Description | Sévérité |
|:---|:---|:---|:---|
| **BR-01** | Isolation Multi-Tenant | Chaque enregistrement lié à une école doit impérativement porter son `organization_id`. | CRITIQUE |
| **BR-02** | Unicité du Matricule | Le matricule d'un étudiant ou professeur est unique au sein de son établissement. | BLOQUANT |
| **BR-03** | Sécurité des Mots de Passe | Mots de passe hashés avec BCrypt (facteur de coût $\ge 12$). | CRITIQUE |
| **BR-04** | Intégrité des Évaluations | Une note est comprise entre 0 et 20 et ne peut être modifiée après clôture du trimestre. | RÈGLE MÉTIER |
| **BR-05** | Audit Trail | Toute action d'écriture ou de suppression fait l'objet d'un log immuable dans `audit_logs`. | AUDIT |

---

## 5. 📂 Registre des Spécifications Modulaires (Features)

| ID Feature | Titre de la Fonctionnalité | Fichier Détaillé | Statut |
| :--- | :--- | :--- | :---: |
| **FEAT-001** | Authentification & Onboarding Multi-Tenant | [`FEAT-001-auth-onboarding.md`](file:///home/pmt/Téléchargements/papa-221-main/bou%20bakh/docs/requirements/FEAT-001-auth-onboarding.md) | `APPROVED` ✅ |
| **FEAT-002** | Gestion Administrative des Étudiants | `docs/requirements/FEAT-002-students.md` *(fichier absent)* | `MANQUANT — à rédiger` ⚠️ |
| **FEAT-003** | Espace Professeur & Saisie des Notes | `docs/requirements/FEAT-003-professors.md` *(fichier absent)* | `MANQUANT — à rédiger` ⚠️ |
| **FEAT-004** | Planification & Emplois du Temps | `docs/requirements/FEAT-004-planning.md` *(fichier absent)* | `MANQUANT — à rédiger` ⚠️ |
| **FEAT-005** | Contrôle d'Accès Campus & Badges QR | `docs/requirements/FEAT-005-security.md` *(fichier absent)* | `MANQUANT — à rédiger` ⚠️ |
| **FEAT-006** | Espace Parent (suivi des enfants, RDV, justification d'absence) | [`FEAT-006-espace-parent.md`](docs/requirements/FEAT-006-espace-parent.md) | `DRAFT` 📝 |

> **Note d'assainissement (2026-11-09, Agent 01)** : FEAT-002 à FEAT-005 étaient affichées `APPROVED` alors qu'aucun fichier correspondant n'existe dans `docs/requirements/` (constat Agent 05, revérifié : le dossier ne contient que `FEAT-001-auth-onboarding.md` avant ajout de FEAT-006). Leur statut est corrigé en `MANQUANT — à rédiger` ; aucune de ces spécifications ne doit être considérée comme validée (Gate 1 non franchie) tant que son fichier n'a pas été rédigé puis approuvé par le Tech Lead.
