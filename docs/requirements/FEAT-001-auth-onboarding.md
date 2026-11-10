# 📋 Spécification Fonctionnelle : FEAT-001 — Authentification & Onboarding Multi-Tenant

| Métadonnée | Valeur |
| :--- | :--- |
| **Identifiant** | FEAT-001 |
| **Auteur** | Agent 01 — Product Analyst |
| **Validé par (Tech Lead)** | ✅ Validé le 2026-11-05 |
| **Statut** | APPROVED |
| **Version** | v1.0 |

---

## 1. Contexte & Valeur Métier
- **Problématique & Objectif** : Permettre à tout établissement scolaire de s'enregistrer de façon autonome sur la plateforme École 221 et d'offrir une porte d'entrée sécurisée avec délivrance de jeton JWT pour tous les profils utilisateurs.
- **Acteurs Cibles** : SuperAdmin (plateforme globale), Responsable d'école (création tenant), Utilisateurs généraux (Admin, Enseignant, Étudiant, Parent, Vigil).

---

## 2. Périmètre (Scope)
### ✅ Dans le Périmètre (In-Scope)
- Authentification unifiée par email / mot de passe (`POST /api/auth/login-token`).
- Récupération du profil utilisateur authentifié (`GET /api/auth/me`).
- Inscription autonome d'une nouvelle école avec génération de slug unique (`POST /api/register-school`).
- Déconnexion avec invalidation du contexte de session (`POST /api/auth/logout`).

### ❌ Hors Périmètre (Out-of-Scope)
- Authentification biométrique / Social Login (Google, Microsoft) reportée aux versions futures.
- Réinitialisation de mot de passe par SMS (seul l'email transactionnel est pris en compte).

---

## 3. Dictionnaire de Données Métier

| Entité Métier | Attribut Métier | Type / Format Naturel | Obligatoire ? | Description & Contraintes Métier |
| :--- | :--- | :--- | :---: | :--- |
| **Utilisateur** | Email | Adresse email valide | Oui | Identifiant unique de connexion sur la plateforme |
| **Utilisateur** | Mot de passe | Texte masqué | Oui | 8 caractères min, 1 majuscule, 1 chiffre, 1 caractère spécial |
| **Utilisateur** | Rôle | Énumération | Oui | `SUPER_ADMIN`, `ADMIN`, `PROFESSEUR`, `ETUDIANT`, `PARENT`, `VIGIL` |
| **Établissement** | Nom école | Texte (3 à 100 car.) | Oui | Raison sociale de l'école (ex: Lycée d'Excellence Dakar) |
| **Établissement** | Slug | Texte alphanumérique | Oui | Identifiant URL unique (ex: `lycee-excellence-dakar`) |
| **Établissement** | Statut | Énumération | Oui | `PENDING` (en attente), `ACTIVE` (validée), `SUSPENDED` |

---

## 4. Matrice des Règles Métier (Business Rules)

| Réf Règle | Intitulé | Description Stricte | Sévérité |
| :--- | :--- | :--- | :---: |
| **FEAT-001-BR-01** | Isolation Multi-Tenant | Chaque utilisateur d'établissement est rattaché à son `organization_id` immuable. | BLOQUANT |
| **FEAT-001-BR-02** | Unicité du Slug | Deux écoles ne peuvent avoir le même slug d'accès. | BLOQUANT |
| **FEAT-001-BR-03** | Chiffrement Mots de Passe | Mots de passe hashés avec BCrypt (facteur de coût $\ge 12$). | BLOQUANT |
| **FEAT-001-BR-04** | Activation SuperAdmin | Un établissement créé reste `PENDING` jusqu'à validation de l'abonnement par le SuperAdmin. | MAJEUR |
| **FEAT-001-BR-05** | Audit Connexions | Tout échec ou succès d'authentification génère un événement dans `audit_logs`. | MAJEUR |

---

## 5. User Stories & Scénarios d'Acceptation (Gherkin en Français)

### User Story [FEAT-001-US-01] : Connexion & Obtention du Jeton JWT
> **En tant qu'** utilisateur de la plateforme École 221  
> **Je veux** me connecter avec mes identifiants valides  
> **Afin d'** accéder à mes outils académiques et administratifs  
> **Règles associées** : `FEAT-001-BR-01`, `FEAT-001-BR-03`, `FEAT-001-BR-05`

#### Scénarios d'Acceptation :

Scénario: [FEAT-001-SC-01] Connexion réussie avec identifiants valides
  Étant donné un compte utilisateur existant et actif
  Et que le mot de passe saisi correspond au hash stocké
  Quand la demande de connexion est soumise
  Alors le système génère un jeton JWT signé avec les permissions du rôle
  Et enregistre une entrée de succès dans les logs d'audit
  Et redirige l'utilisateur vers son tableau de bord spécifique

Scénario: [FEAT-001-SC-02] Rejet en cas d'identifiants erronés
  Étant donné une tentative avec un mot de passe incorrect
  Quand la demande de connexion est soumise
  Alors le système refuse l'accès avec un code d'erreur 401
  Et consigne l'adresse IP et la tentative infructueuse dans le journal de sécurité
  Et n'indique pas si l'email existe pour prévenir l'énumération de comptes

---

### User Story [FEAT-001-US-02] : Inscription d'un Établissement (Onboarding)
> **En tant que** responsable d'école  
> **Je veux** enregistrer mon établissement et créer mon compte administrateur  
> **Afin de** démarrer la gestion de mon établissement  
> **Règles associées** : `FEAT-001-BR-02`, `FEAT-001-BR-04`

#### Scénarios d'Acceptation :

Scénario: [FEAT-001-SC-03] Enregistrement nominal d'une école
  Étant donné un nom d'école, un slug unique disponible et un email valide
  Quand le formulaire d'inscription est validé
  Alors le système réserve l'organisation avec son identifiant unique
  Et initialise le compte administrateur associé
  Et attribue à l'établissement le statut initial PENDING

Scénario: [FEAT-001-SC-04] Rejet si le slug de l'école existe déjà
  Étant donné un slug déjà utilisé par un autre établissement
  Quand la demande d'inscription est soumise
  Alors le système rejette la création avec un message explicite de conflit
  Et invite l'utilisateur à personnaliser son slug

---

## 6. Exigences Non-Fonctionnelles (NFR)
- **Performance** : Temps de réponse pour la délivrance du JWT $< 250$ms.
- **Sécurité & Confidentialité** : Durée de vie du token JWT limitée à 24 heures, signature HMAC-SHA384 minimum.
- **Volumétrie Attendue** : Capacité initiale de 50 établissements et 10 000 connexions quotidiennes simultanées.
- **Audit & Traçabilité** : Chaque échec d'authentification doit inscrire l'adresse IP, l'identifiant tenté et le User-Agent dans `audit_logs`.

---

## 7. ❓ Hypothèses & Points à Confirmer
- [x] *(Résolu)* Le slug de l'école est généré automatiquement à partir de son nom lors de la saisie, mais modifiable par l'utilisateur.

---

## 8. 📝 Historique des Révisions (Changelog)
| Date | Version | Auteur | Nature des Modifications |
| :--- | :---: | :--- | :--- |
| 2026-11-05 | v1.0 | Agent 01 | Spécification initiale validée lors de la phase d'audit |
