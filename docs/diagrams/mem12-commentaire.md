# MEM-12 — Classes et base de données du cœur métier (chapitre 4)

- **Statut** : TEL QUE CONSTRUIT (sélection manuelle tirée du code ; aucune classe ni aucun lien inventé)
- **Diagramme** : `docs/diagrams/mem12-classes-bd.puml` → rendu `docs/diagrams/png/mem12-classes-bd.png`
- **Sources** : entités du domaine et entités JPA du backend (références `fichier:ligne` ci-dessous).
  Préfixe omis : `backend/src/main/java/ecole_221/sn/ecole/`
- **Date** : 2026-11-09 — Agent 11 (Seynabou Cissé)
- **Référence exhaustive** : les diagrammes générés `docs/diagrams/generated/classes-*.puml` et `bd-*.puml`
  (`diagrams-check` le 2026-11-09 : « 36/36 diagramme(s) à jour »). Le diagramme MEM-12 n'est qu'un extrait
  commenté pour le mémoire : il ne les remplace pas.

---

## 1. Pourquoi ces classes (et pas les autres)

Le backend compte une quarantaine d'entités JPA (36 diagrammes générés). Pour le chapitre 4, on ne retient
que les classes qui répondent à **une** question : *comment une même plateforme sert-elle plusieurs écoles
sans mélanger leurs données ?* Elles forment trois groupes :

| Groupe | Classes | Rôle dans la démonstration |
|---|---|---|
| Socle multi-école | `Organization`, `OrganizationUser`, `User` (+ `TenantProfile`) | Qui est l'école, qui est l'utilisateur, et le lien d'appartenance entre les deux |
| Métier « famille » | `Parent`, `ParentEnfant` | Exemple de données propres à une école (lien parent ↔ enfant) |
| Métier « pédagogie / admission » | `Course`, `GradeJpaEntity`, `Candidate` | Exemples de tables isolées par école, avec comportements métier (`Candidate`) |

Écartés volontairement : finance, planning, collaboration, notifications, audit, dashboard… (ils suivent le
même schéma d'isolation et figurent dans `generated/`).

**Adaptation assumée** : il n'existe **pas** de classe de domaine `Grade` ; seule l'entité de persistance
`GradeJpaEntity` existe (`modules/professor/infrastructure/persistence/GradeJpaEntity.java:7-24`).
Elle est donc montrée telle quelle, avec un stéréotype « pas de modèle domaine ».

## 2. Traçabilité des classes

| Classe (diagramme) | Domaine (attributs / méthodes) | Persistance (table, isolation) |
|---|---|---|
| `Organization` | `modules/platform/organization/domain/model/Organization.java:14-40` ; méthodes `validate/suspend/reactivate/archive/unarchive/isActive` l.172-215 | `.../infrastructure/persistence/OrganizationJpaEntity.java:11` table `organizations` ; **pas** de `@TenantId` (absente de la recherche `@TenantId`) |
| `OrganizationUser` | `.../domain/model/OrganizationUser.java:16-29` ; `activate/suspend/expire` l.107-124, `hasPermission/addPermission/removePermission` l.140-161 | `.../persistence/OrganizationUserJpaEntity.java:11` table `organization_users` ; `user_id` l.17-18, `organization_id` l.20-21 **colonne simple, non `@TenantId`** |
| `User` | `modules/auth/domain/model/User.java:21-39` ; `addTenantProfile` l.114, `changePassword` l.156, `recordLogin` l.163, `isAdmin` l.192 | `modules/auth/infrastructure/persistence/UserJpaEntity.java:10` table `users` ; pas de `@TenantId` ; écouteur `UserMembershipListener` (SEC-003) l.11-12 |
| `TenantProfile` | `modules/auth/domain/valueobject/TenantProfile.java:8-11` (`tenantId`, `role`) | — (objet valeur, porté par `User.tenantProfiles`, `User.java:30`) |
| `Parent` | `modules/parent/domain/model/Parent.java:9-19`, `create` l.37 | `.../parent/infrastructure/persistence/ParentJpaEntity.java:7-9` table `parents`, `@TenantId` |
| `ParentEnfant` | `modules/parent/domain/model/ParentEnfant.java:8-13` | `.../ParentEnfantJpaEntity.java:7-11` table `parent_enfant`, `@TenantId` sur `organization_id` |
| `Course` | `modules/professor/domain/model/Course.java:13-21` | `.../professor/infrastructure/persistence/CourseJpaEntity.java:8-12` table `courses`, `@TenantId` |
| `GradeJpaEntity` | (aucun modèle domaine) | `.../professor/infrastructure/persistence/GradeJpaEntity.java:8-24` table `grades`, `@TenantId` l.10-12 |
| `Candidate` | `modules/admissions/domain/model/Candidate.java:11-20` ; `accept/reject/markAsInProgress/finalizeStatus` l.84-96, `hasPassed` l.112 | `.../admissions/infrastructure/persistence/CandidateJpaEntity.java:10-12` table `candidates`, `@TenantId` |

**Liens** : un seul lien est une référence objet réelle : `User *-- TenantProfile` (`User.java:30`,
`List<TenantProfile>`). Tous les autres sont des identifiants `String` (`userId`, `organizationId`,
`parentId`, `enfantId`, `profId`, `courseId`, `studentId`) : ils sont dessinés **en pointillés et marqués
« déduit »**. Preuve : la recherche `@(ManyToOne|OneToMany|ManyToMany|OneToOne|JoinColumn)` dans
`backend/src/main/java` ne trouve que `GroupChatJpaEntity.java:47,54` (hors périmètre MEM-12).
Pour `enfantId` et `studentId`, la table cible (utilisateur élève ? `StudentData` ?) n'est pas déterminable
par le code lu : marqué « élève ? ».

## 3. Le choix multi-école : `organization_id`, `@TenantId`, `organization_users`

1. **Une base, une colonne de discrimination.** Les tables métier portent une colonne `organization_id`
   annotée `@org.hibernate.annotations.TenantId` (ex. `CourseJpaEntity.java:10-12`,
   `GradeJpaEntity.java:10-12`, `ParentEnfantJpaEntity.java:9-11`). Hibernate renseigne cette colonne à
   l'écriture et ajoute le filtre à la lecture, à partir de la valeur fournie par
   `shared/infrastructure/tenant/HibernateTenantIdentifierResolver.java:7-19` (lue dans `TenantContext`).
   Le code métier n'a donc pas à écrire `WHERE organization_id = ?` lui-même.
2. **Le domaine reste ignorant de l'école.** `organization_id` est dans l'entité JPA, pas dans les classes
   du domaine (`Course.java:15-21` n'a pas ce champ) : l'isolation est une préoccupation d'infrastructure.
3. **Comptes globaux, appartenance explicite.** `users` et `organizations` n'ont pas de `@TenantId` :
   une même personne peut appartenir à plusieurs écoles. Le lien est la table `organization_users`
   (`OrganizationUser.java:12-14` : « Un utilisateur peut avoir plusieurs memberships »), qui porte le rôle,
   les permissions, la portée (`scopeType`, `scopeId`) et le statut de l'adhésion. Sa colonne
   `organization_id` n'est **pas** `@TenantId` (`OrganizationUserJpaEntity.java:20-21`), ce qui permet de
   retrouver toutes les écoles d'un utilisateur (hypothèse : nécessaire à la connexion ; à confirmer par l'Agent 02).
4. **Doublon de modélisation à noter** : l'appartenance est aussi portée côté `User` par
   `tenantProfiles : List<TenantProfile>` (`User.java:30`, `TenantProfile.java:10-11`). Deux représentations
   du même fait coexistent (constat, pas de jugement : à arbitrer par l'Agent 02).

## 4. Limites constatées (à écrire telles quelles dans le mémoire)

- **Schéma sans migrations versionnées.** `application.yaml:46` : `ddl-auto: update` ; `application.yaml:61-62` :
  `flyway.enabled: false`, alors que Flyway est une dépendance (`backend/pom.xml:108-113`). Le code le reconnaît
  (`modules/referential/infrastructure/config/ReferenceDataSeeder.java:19` : « Flyway étant désactivé
  (ddl-auto: update) »). Conséquence : le schéma réel est celui que Hibernate déduit des entités ; ni l'historique
  ni les contraintes de base (clés étrangères, index) ne sont versionnés. Les tests utilisent `create-drop`
  (`backend/src/test/resources/application-test.yaml:22`).
- **Pas d'intégrité référentielle déclarée côté ORM** : aucun `@ManyToOne` sur les tables du cœur métier (voir §2).
- **Données encore fictives / valeurs par défaut factices** :
  - `User.java:51` : tout utilisateur sans matricule reçoit la même valeur codée en dur (`"2026-EC-001"`).
  - `Course.java:34-35` : `code` et `description` par défaut `"DEFAULT-CODE"` / `"Description par défaut"`.
  - `modules/student/infrastructure/persistence/CourseDetailInitializer.java:11-32` : composant **actif**
    (`@Component`) qui insère au démarrage un contenu de cours de démonstration si la table est vide.
  - En revanche `infrastructure/config/DataInitializer.java:21-28` est **inactif** (annotation `@Component`
    retirée, commentaire APP-SEC-10).
- **Grade sans modèle domaine** (voir §1), contrairement aux autres agrégats.

## 5. Anomalies signalées (Agent 02 — non corrigées ici)

| # | Constat (fait) | Preuve | Question |
|---|---|---|---|
| A1 | Le résolveur renvoie `""` quand aucune école n'est définie, et les branches « mode plateforme » / « mode école » sont identiques | `HibernateTenantIdentifierResolver.java:11-18` | Une requête hors contexte école lit-elle/écrit-elle sous `organization_id = ''` ? Comportement voulu ? |
| A2 | `ddl-auto: update` en configuration principale, Flyway désactivé | `application.yaml:46,61-62` | Plan de passage aux migrations versionnées ? |
| A3 | Liens inter-tables uniquement par `String` | §2 | Contraintes FK attendues en base ? |
| A4 | Appartenance en double (`organization_users` et `User.tenantProfiles`) | `OrganizationUser.java:16-20`, `User.java:30` | Laquelle fait foi ? |
| A5 | Colonne `role_id` en base absente du modèle domaine `OrganizationUser` | `OrganizationUserJpaEntity.java:26-27` vs `OrganizationUser.java:18-29` | Champ en cours d'introduction ? |
| A6 | Matricule par défaut identique pour tous ; initialiseur de démonstration actif | `User.java:51`, `CourseDetailInitializer.java:11` | À neutraliser avant données réelles ? |

## 6. Rendu

- `diagrams-render` : premier essai en erreur (ligne 93 : guillemets « » dans un nom de paquet, corrigé) ;
  second essai : code de sortie 0, fichier `docs/diagrams/png/mem12-classes-bd.png` présent.
- **Non‑troncature : non vérifiée visuellement** (mes outils ne lisent pas les images). Le diagramme compte
  9 classes, 5 paquets et 2 notes, a priori sous la limite par défaut de PlantUML (4096 px) : c'est une
  **hypothèse**, à confirmer à l'œil avant insertion dans le mémoire.
- Aucune donnée sensible : pas de nom réel, d'email, d'URL de base ni de secret (le matricule cité est la
  valeur par défaut du code, non une donnée personnelle).
