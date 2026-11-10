# 📋 Spécification Fonctionnelle : FEAT-003 — Espace Professeur & Saisie des Notes

| Métadonnée | Valeur |
| :--- | :--- |
| **Identifiant** | FEAT-003 |
| **Auteur** | Agent 01 — Product Analyst |
| **Validé par (Tech Lead)** | ⏳ En attente |
| **Statut** | DRAFT |
| **Version** | v1.0 |

> **Méthode (rétro-spécification)** : ce document décrit le comportement **constaté dans le code réel** au 2026-11-09, puis le comportement **cible** quand il diffère. Chaque règle porte un état d'implémentation :
> - ✅ **RÉEL** : comportement présent dans le code (preuve `fichier:ligne`).
> - ⚠️ **PARTIEL** : présent sur une partie des points d'entrée seulement, ou avec un écart.
> - ❌ **NON RÉEL** : absent du code ; la règle est une **cible** soumise à validation. Les scénarios correspondants échoueront aujourd'hui.
>
> Chemins de preuve (abrégés) : `PC` = `backend/.../modules/professor/infrastructure/web/ProfessorController.java`, `PEC` = `.../web/ProfExtraController.java`, `PS` = `.../application/service/ProfessorService.java`, `PRA` = `.../infrastructure/persistence/ProfessorRepositoryAdapter.java`, `GD` = `.../application/port/dto/GradeDto.java`, `SC` = `backend/.../infrastructure/config/SecurityConfig.java`.

---

## 1. Contexte & Valeur Métier
- **Problématique & Objectif** : donner au professeur un espace unique pour consulter ses cours et son emploi du temps, saisir les notes (contrôle continu et examen), gérer ses séances (annulation, report), publier devoirs, quiz, leçons, modules et rappels, et faire l'appel. Gain pour l'école : notes et présences disponibles sans ressaisie, moyenne calculée de façon homogène, séances modifiées tracées.
- **Acteurs Cibles** :
  - **Professeur** (rôles `PROFESSEUR` / `TEACHER`) : acteur principal.
  - **Admin Établissement** (`ADMIN` / `ADMINISTRATOR`) et **SuperAdmin** (`SUPER_ADMIN`) : accès à l'espace professeur (SC:108) et dérogation sur l'annulation / le report de toutes les séances de l'école (PEC:215-227).
  - **Étudiant** : bénéficiaire indirect (notes, présences, devoirs).

---

## 2. Périmètre (Scope)
### ✅ Dans le Périmètre (In-Scope)
- Consultation paginée de **ses** cours (identité issue de l'authentification).
- Consultation de **son** emploi du temps (deux points d'entrée existent : « planning » et « emploi du temps du jour »).
- Consultation des notes d'un cours ; saisie / modification de la note de contrôle continu et/ou d'examen d'un étudiant ; calcul de la moyenne et de la mention.
- Annulation (avec motif) et report (jour, heure, salle) de **ses** séances ; dérogation des administrateurs.
- Devoirs : création et consultation paginée par cours.
- Quiz : création et consultation, rattachés à un cours ou à un module.
- Leçons, modules et rappels d'un cours : création et consultation (décrits au dictionnaire ; règles minimales).
- Présences : consultation de la liste d'étudiants d'une classe / d'un cours et soumission d'une feuille de présence (un relevé ou une liste).

### ❌ Hors Périmètre (Out-of-Scope)
- Génération des bulletins, coefficients par matière et moyenne générale (relèvent d'une feature « bulletins » à spécifier).
- Correction / passage des quiz par les étudiants, rendu des devoirs (espace Étudiant, FEAT-002).
- Création des cours, affectation professeur ↔ cours et construction de l'emploi du temps (relèvent de l'Admin / FEAT-004 Planification).
- Détection de conflits de salle lors d'un report (FEAT-004) — voir question Q5.
- Notification automatique des étudiants / parents lors d'une annulation ou d'un report.
- Modification / suppression des devoirs, quiz, leçons, modules, présences (aucune capacité dans le code ; non demandée).

---

## 3. Dictionnaire de Données Métier

| Entité Métier | Attribut Métier | Type / Format Naturel | Obligatoire ? | Description & Contraintes Métier |
| :--- | :--- | :--- | :---: | :--- |
| **Cours** | Identifiant | Texte | Oui | Attribué par le système |
| **Cours** | Intitulé, code, description | Texte | Intitulé : Oui | Libellés du cours |
| **Cours** | Classe | Texte | Oui | Classe destinataire (ex. « M1 GL ») |
| **Cours** | Volume horaire total | Entier (heures) | Non | |
| **Cours** | Professeur titulaire | Référence Utilisateur | Oui | Sert à filtrer « mes cours » |
| **Cours** | École | Référence Établissement | Oui | Isolation multi-tenant |
| **Note** | Étudiant, Cours | Références | Oui | Au plus une note par couple étudiant / cours (mise à jour si elle existe, PRA:135-136) |
| **Note** | Contrôle continu (CC) | Décimal sur 20 | Non* | Entre 0 et 20 inclus ; *au moins CC ou Examen doit être fourni |
| **Note** | Examen | Décimal sur 20 | Non* | Entre 0 et 20 inclus |
| **Note** | Moyenne | Décimal arrondi au centième | Calculée | 40 % CC + 60 % Examen (voir BR-04 et Q1) |
| **Note** | Mention | Lettre A / B / C / D / F | Calculée | A ≥ 16, B ≥ 14, C ≥ 12, D ≥ 10, sinon F (GD:52-58) |
| **Séance** | Identifiant, intitulé du cours, classe, type | Texte | Oui | Créneau de l'emploi du temps |
| **Séance** | Jour, heure, salle | Texte | Oui | Modifiés par un report |
| **Séance** | Professeur | Référence Utilisateur | Oui | Détermine « mes séances » |
| **Séance** | Statut | Énumération | Oui | Valeurs constatées : « annulé », « reporté » (PS:133, PS:145) ; valeur initiale non documentée |
| **Séance** | Motif d'annulation | Texte | Oui si annulée | Voir BR-07 |
| **Séance** | Date d'origine | Date-heure | Non | ⚠️ Renseignée avec l'instant du report et non la date initiale de la séance (PS:146) |
| **Devoir** | Titre | Texte | Oui | Non vide |
| **Devoir** | Description | Texte | Non | |
| **Devoir** | Priorité | Énumération | Oui | Valeurs de l'énumération du code (à lister par l'Agent 02) |
| **Devoir** | Date limite | Date | Oui | Non vide |
| **Quiz** | Titre | Texte | Oui | Non vide |
| **Quiz** | Durée | Entier (minutes) | Oui | Aucune borne contrôlée |
| **Quiz** | Rattachement | Cours ou Module | Oui | ⚠️ Un module et un cours sont stockés dans le même champ de rattachement (PEC:62, PEC:82, PRA:244) |
| **Leçon** | Titre, durée (min), date | Texte / Entier / Date | Oui | |
| **Module** | Nom | Texte | Oui | |
| **Rappel** | Contenu, urgence | Texte / Oui-Non | Oui | Échéance fixée par défaut à +7 jours (PS:116) |
| **Présence** | Date, étudiant (identifiant + nom), statut, cours | Date / Référence / Énumération / Référence | Oui (cible) | ❌ Aujourd'hui non contrôlés (BR-13) |

---

## 4. Matrice des Règles Métier (Business Rules)

| Réf Règle | Intitulé | Description Stricte | Sévérité | État (preuve) |
| :--- | :--- | :--- | :---: | :--- |
| **FEAT-003-BR-01** | Identité issue de l'authentification | « Mes cours » et « mon emploi du temps » sont déterminés exclusivement par l'utilisateur authentifié ; aucun identifiant de professeur n'est accepté en entrée. Requête non authentifiée : refus (non authentifié). | BLOQUANT | ✅ RÉEL (PC:51-54, PC:265-268, PEC:150-153, PEC:207-213) |
| **FEAT-003-BR-02** | Note : au moins une composante | Une saisie doit contenir une note « cc » et/ou une note « examen ». Sinon refus « requête invalide » avec message « Note manquante : champs attendus « cc » et/ou « examen » ». Aucune note enregistrée. | BLOQUANT | ✅ RÉEL (PC:126, PC:380-384) |
| **FEAT-003-BR-03** | Note : bornes | Chaque note fournie est un nombre compris entre 0 et 20 inclus. Hors intervalle ou non numérique : refus « requête invalide » avec message « Note « champ » hors de l'intervalle 0–20 ». | BLOQUANT | ✅ RÉEL (PC:385-390) |
| **FEAT-003-BR-04** | Moyenne pondérée | Moyenne = 40 % CC + 60 % Examen, arrondie au centième. | BLOQUANT | ⚠️ PARTIEL : exact quand les deux notes existent (PRA:144-147, GD:42-47). Si une seule note existe, deux calculs divergent (voir Q1). |
| **FEAT-003-BR-05** | Mention | Mention A (≥ 16), B (≥ 14), C (≥ 12), D (≥ 10), F (< 10), calculée sur la moyenne affichée. | MINEUR | ✅ RÉEL (GD:52-58) — barème à confirmer (H-02) |
| **FEAT-003-BR-06** | Annulation / report réservés au titulaire | Un professeur ne peut annuler ou reporter que les séances de son propre emploi du temps. Sinon refus « interdit » avec message « Cette séance n'est pas la vôtre ». Les rôles ADMIN, ADMINISTRATOR, SUPER_ADMIN (et PLATFORM_ADMIN) sont exemptés. | BLOQUANT | ✅ RÉEL sur les 4 points d'entrée (PC:287, PC:306, PEC:172, PEC:193, PEC:222-237) |
| **FEAT-003-BR-07** | Motif d'annulation obligatoire | Toute annulation porte un motif non vide. | MAJEUR | ⚠️ PARTIEL : imposé sur « emploi du temps » (PEC:168 + validation du motif), non imposé sur « planning » (PC:284, corps libre) |
| **FEAT-003-BR-08** | Report complet | Un report précise le nouveau jour, la nouvelle heure et la nouvelle salle, tous non vides. | MAJEUR | ⚠️ PARTIEL : imposé sur « emploi du temps » (PEC:188), non imposé sur « planning » (PC:302) |
| **FEAT-003-BR-09** | Contenus limités aux cours du professeur | Un professeur ne peut consulter / saisir notes, devoirs, quiz, leçons, modules, rappels et présences que sur les cours dont il est titulaire (administrateurs exemptés). | BLOQUANT | ❌ NON RÉEL : aucun contrôle d'appartenance du cours (PC:101-259, PEC:32-89) |
| **FEAT-003-BR-10** | Étudiant rattaché au cours | Une note ou une présence ne peut concerner qu'un étudiant inscrit au cours / à la classe concernée. | BLOQUANT | ❌ NON RÉEL (PRA:134-149, PRA:264-273) |
| **FEAT-003-BR-11** | Isolation multi-tenant | Toutes les données de l'espace professeur sont limitées à l'école de l'utilisateur, y compris les listes d'étudiants. | BLOQUANT | ⚠️ PARTIEL : cours, notes, devoirs, leçons, modules, quiz, rappels, séances et présences sont cloisonnés par école (marqueur d'école sur chaque entité, ex. `GradeJpaEntity.java:10`). Les **listes d'étudiants** sont lues par rôle sans filtre d'école (PC:76-77, PRA:82 ; l'entité Utilisateur ne porte pas ce marqueur) → fuite inter-écoles **probable**, à confirmer par test (Agent 05/06). |
| **FEAT-003-BR-12** | Devoir et quiz valides | Devoir : titre et date limite non vides, priorité dans la liste autorisée. Quiz : titre non vide, durée en minutes. | MAJEUR | ✅ RÉEL (validations des requêtes de création devoir / quiz) ; ❌ aucune borne sur la durée |
| **FEAT-003-BR-13** | Présence complète | Chaque relevé de présence contient date, étudiant, statut (valeur d'une liste fermée) et cours ; sinon refus du relevé. | BLOQUANT | ❌ NON RÉEL : valeurs par défaut codées en dur (date « 2026-07-20 », cours « course-1 ») si absentes, statut libre (PEC:125-126) ; un modèle de validation existe mais n'est pas utilisé |
| **FEAT-003-BR-14** | Traçabilité | Saisie de note, annulation, report, création de devoir/quiz/présence génèrent une trace immuable (auteur = utilisateur authentifié) dans le journal d'audit de l'école. | MAJEUR | ⚠️ PARTIEL : trace **applicative** uniquement (journal technique, pas `audit_logs` : aucun accès au stockage dans `infrastructure/logging/`) pour note (PC:132), annulation/report via « planning » (PC:289, PC:308), rappel (PC:346). Aucune trace pour les points d'entrée « emploi du temps », devoirs, quiz, leçons, modules, présences. |
| **FEAT-003-BR-15** | Rôles autorisés | L'espace professeur est réservé aux rôles PROFESSEUR, TEACHER, ADMIN, ADMINISTRATOR, SUPER_ADMIN. Tout autre rôle (étudiant, parent, vigil) est refusé. | BLOQUANT | ✅ RÉEL (SC:108) |
| **FEAT-003-BR-16** | Saisie partielle sans perte | Saisir uniquement la note d'examen ne doit pas effacer une note de CC déjà enregistrée (et inversement). | MAJEUR | ❌ NON RÉEL : la composante non fournie est remplacée par « vide » (PRA:142-143) — voir Q2 |
| **FEAT-003-BR-17** | Liste d'étudiants fidèle | La liste d'étudiants d'un cours / d'une classe reflète les inscrits réels et leur situation réelle. | MAJEUR | ❌ NON RÉEL : la classe demandée est ignorée (« M1 GL » codé en dur, PEC:98, puis ignoré PRA:81-82) ; statut « PRESENT » et note 15,0 codés en dur pour chaque étudiant d'un cours (PC:86-87) |

---

## 5. User Stories & Scénarios d'Acceptation (Gherkin en Français)

> Les scénarios marqués **[CIBLE]** décrivent un comportement non encore implémenté : ils échoueront tant que la règle correspondante est ❌/⚠️.

### User Story [FEAT-003-US-01] : Consulter mes cours et mon emploi du temps
> **En tant que** Professeur  
> **Je veux** voir uniquement mes cours et mes séances  
> **Afin de** préparer mon enseignement sans voir ni modifier le planning de mes collègues  
> **Règles associées** : `FEAT-003-BR-01`, `FEAT-003-BR-11`, `FEAT-003-BR-15`

```gherkin
Scénario: [FEAT-003-SC-01] Cas nominal — Mes cours, paginés
  Étant donné que le professeur P1 de l'école A est authentifié
  Et que P1 est titulaire de 3 cours et son collègue P2 de 2 cours
  Quand P1 consulte ses cours (page 1, 10 éléments par page)
  Alors seuls les 3 cours de P1 sont retournés avec le nombre total d'éléments

Scénario: [FEAT-003-SC-02] Cas nominal — Mon emploi du temps
  Étant donné que le professeur P1 est authentifié
  Quand P1 consulte son emploi du temps
  Alors seules les séances dont P1 est le professeur sont retournées
  Et aucun identifiant de professeur saisi par l'utilisateur n'est pris en compte

Scénario: [FEAT-003-SC-03] Cas d'erreur — Utilisateur non authentifié
  Étant donné qu'aucune session n'est ouverte
  Quand une consultation des cours ou de l'emploi du temps est demandée
  Alors la demande est refusée comme non authentifiée
  Et aucune donnée n'est retournée

Scénario: [FEAT-003-SC-04] Cas d'erreur — Rôle non autorisé
  Étant donné qu'un étudiant (ou un parent, ou un vigil) est authentifié
  Quand il tente d'accéder à l'espace professeur
  Alors l'accès est refusé (interdit)

Scénario: [FEAT-003-SC-05] Cas d'isolation Multi-Tenant
  Étant donné qu'un professeur authentifié appartient à l'école A
  Quand il consulte ses cours et son emploi du temps
  Alors aucun cours ni aucune séance de l'école B n'apparaît
```

### User Story [FEAT-003-US-02] : Saisir les notes d'un étudiant
> **En tant que** Professeur  
> **Je veux** saisir la note de contrôle continu et/ou d'examen d'un étudiant sur 20  
> **Afin d'** obtenir automatiquement sa moyenne et sa mention  
> **Règles associées** : `FEAT-003-BR-02`, `FEAT-003-BR-03`, `FEAT-003-BR-04`, `FEAT-003-BR-05`, `FEAT-003-BR-09`, `FEAT-003-BR-10`, `FEAT-003-BR-11`, `FEAT-003-BR-14`, `FEAT-003-BR-16`

```gherkin
Scénario: [FEAT-003-SC-06] Cas nominal — Saisie CC et examen
  Étant donné que le professeur P1 est authentifié
  Et que l'étudiant E1 n'a pas encore de note dans le cours C1
  Quand P1 saisit pour E1 dans C1 une note de CC de 12 et une note d'examen de 17,5
  Alors la note est enregistrée
  Et la moyenne vaut 15,3 (12 × 0,4 + 17,5 × 0,6 = 4,8 + 10,5)
  Et la mention vaut « B »
  Et une trace « SAVE_GRADE » portant l'identifiant de P1 est journalisée

Scénario: [FEAT-003-SC-07] Cas nominal — Arrondi au centième
  Étant donné que le professeur P1 est authentifié
  Quand P1 saisit pour E1 une note de CC de 13,33 et une note d'examen de 14,17
  Alors la moyenne enregistrée et affichée vaut 13,83 (13,834 arrondi au centième)

Scénario: [FEAT-003-SC-08] Cas d'erreur métier — Aucune note fournie
  Étant donné que le professeur P1 est authentifié
  Quand P1 envoie une saisie sans « cc » ni « examen » (par exemple avec un champ « noteCc »)
  Alors la saisie est refusée comme requête invalide
  Et le message indique « Note manquante : champs attendus « cc » et/ou « examen » »
  Et aucune note n'est créée ni modifiée

Scénario: [FEAT-003-SC-09] Cas d'erreur métier — Note hors intervalle
  Étant donné que le professeur P1 est authentifié
  Quand P1 saisit une note d'examen de 21 (ou de -1)
  Alors la saisie est refusée comme requête invalide
  Et le message indique « Note « examen » hors de l'intervalle 0–20 »
  Et la note existante éventuelle reste inchangée

Scénario: [FEAT-003-SC-10] [CIBLE] Saisie partielle sans perte
  Étant donné que l'étudiant E1 a déjà une note de CC de 12 dans le cours C1
  Quand le professeur saisit uniquement une note d'examen de 16
  Alors la note de CC de 12 est conservée
  Et la moyenne vaut 14,4

Scénario: [FEAT-003-SC-11] [CIBLE] Cas d'erreur — Cours d'un autre professeur ou étudiant non inscrit
  Étant donné que le professeur P1 n'est pas titulaire du cours C2
  Quand P1 saisit une note dans C2, ou une note dans C1 pour un étudiant non inscrit à C1
  Alors la saisie est refusée (interdit / requête invalide)
  Et aucune note n'est enregistrée

Scénario: [FEAT-003-SC-12] Cas d'isolation Multi-Tenant
  Étant donné qu'un professeur authentifié appartient à l'école A
  Quand il consulte ou saisit des notes d'un cours de l'école B
  Alors aucune note de l'école B n'est lue ni modifiée
```

### User Story [FEAT-003-US-03] : Annuler ou reporter mes séances
> **En tant que** Professeur  
> **Je veux** annuler (avec motif) ou reporter (jour, heure, salle) une de mes séances  
> **Afin de** tenir l'emploi du temps à jour en cas d'empêchement  
> **Règles associées** : `FEAT-003-BR-06`, `FEAT-003-BR-07`, `FEAT-003-BR-08`, `FEAT-003-BR-11`, `FEAT-003-BR-14`

```gherkin
Scénario: [FEAT-003-SC-13] Cas nominal — Annulation de ma séance
  Étant donné que le professeur P1 est authentifié
  Et que la séance S1 figure dans son emploi du temps
  Quand P1 annule S1 avec le motif « Jury de soutenance »
  Alors S1 passe au statut « annulé » avec ce motif
  Et une trace d'annulation portant l'identifiant de P1 est journalisée

Scénario: [FEAT-003-SC-14] Cas nominal — Report de ma séance
  Étant donné que la séance S1 figure dans l'emploi du temps de P1
  Quand P1 reporte S1 au jeudi, 10h00, salle B12
  Alors S1 porte le nouveau jour, la nouvelle heure, la nouvelle salle et le statut « reporté »

Scénario: [FEAT-003-SC-15] Cas d'erreur métier — Séance d'un collègue
  Étant donné que la séance S2 appartient au professeur P2
  Quand P1 tente d'annuler ou de reporter S2
  Alors la demande est refusée (interdit) avec le message « Cette séance n'est pas la vôtre »
  Et S2 reste inchangée

Scénario: [FEAT-003-SC-16] Cas nominal — Dérogation administrateur
  Étant donné qu'un administrateur de l'école A est authentifié
  Quand il annule la séance S2 du professeur P2 de l'école A
  Alors l'annulation est acceptée

Scénario: [FEAT-003-SC-17] Cas d'erreur métier — Motif ou créneau manquant
  Étant donné que la séance S1 appartient à P1
  Quand P1 annule S1 sans motif, ou la reporte sans salle
  Alors la demande est refusée comme requête invalide et S1 reste inchangée
  # État : vrai sur le point d'entrée « emploi du temps » ; [CIBLE] sur le point d'entrée « planning »

Scénario: [FEAT-003-SC-18] Cas d'isolation Multi-Tenant
  Étant donné qu'un administrateur authentifié appartient à l'école A
  Quand il tente d'annuler une séance de l'école B
  Alors la séance de l'école B n'est ni trouvée ni modifiée
```

### User Story [FEAT-003-US-04] : Publier des devoirs et des quiz
> **En tant que** Professeur  
> **Je veux** créer et consulter les devoirs et quiz de mes cours (et des modules de mes cours)  
> **Afin d'** organiser le travail des étudiants  
> **Règles associées** : `FEAT-003-BR-09`, `FEAT-003-BR-11`, `FEAT-003-BR-12`, `FEAT-003-BR-14`

```gherkin
Scénario: [FEAT-003-SC-19] Cas nominal — Création d'un devoir
  Étant donné que le professeur P1 est titulaire du cours C1
  Quand P1 crée un devoir « TP Docker » avec une priorité et une date limite
  Alors le devoir apparaît dans la liste paginée des devoirs de C1
  Et le message « Devoir créé avec succès » est affiché

Scénario: [FEAT-003-SC-20] Cas nominal — Création d'un quiz dans un cours ou un module
  Étant donné que le professeur P1 est titulaire du cours C1 comportant le module M1
  Quand P1 crée un quiz « Révisions » de 30 minutes dans M1
  Alors le quiz apparaît dans la liste des quiz de M1

Scénario: [FEAT-003-SC-21] Cas d'erreur métier — Titre ou date limite manquant
  Quand P1 crée un devoir sans titre (ou sans date limite), ou un quiz sans titre
  Alors la création est refusée comme requête invalide avec le message de validation correspondant
  Et aucun devoir ni quiz n'est créé

Scénario: [FEAT-003-SC-22] [CIBLE] Cas d'erreur — Cours d'un collègue
  Étant donné que P1 n'est pas titulaire du cours C2
  Quand P1 crée un devoir ou un quiz dans C2
  Alors la création est refusée (interdit)
  Et la tentative est tracée dans le journal d'audit de l'école

Scénario: [FEAT-003-SC-23] Cas d'isolation Multi-Tenant
  Étant donné qu'un professeur authentifié appartient à l'école A
  Quand il consulte les devoirs ou quiz d'un cours de l'école B
  Alors aucun devoir ni quiz de l'école B n'est retourné
```

### User Story [FEAT-003-US-05] : Faire l'appel
> **En tant que** Professeur  
> **Je veux** afficher la liste des étudiants de ma classe et soumettre leurs présences  
> **Afin de** suivre l'assiduité et alimenter le suivi des absences (espace Parent, FEAT-006)  
> **Règles associées** : `FEAT-003-BR-09`, `FEAT-003-BR-10`, `FEAT-003-BR-11`, `FEAT-003-BR-13`, `FEAT-003-BR-14`, `FEAT-003-BR-17`

```gherkin
Scénario: [FEAT-003-SC-24] Cas nominal — Soumission d'une feuille de présence
  Étant donné que le professeur P1 est titulaire du cours C1
  Quand P1 soumet une liste de relevés (date, étudiant, statut, cours) pour C1
  Alors chaque relevé est enregistré
  Et le message « Présences soumises avec succès » est affiché

Scénario: [FEAT-003-SC-25] [CIBLE] Cas d'erreur métier — Relevé incomplet
  Quand P1 soumet un relevé sans date, sans cours ou avec un statut hors liste
  Alors le relevé est refusé comme requête invalide
  Et aucune date ni aucun cours par défaut n'est enregistré à sa place

Scénario: [FEAT-003-SC-26] [CIBLE] Liste fidèle des étudiants de la classe
  Étant donné que la classe « L3 GL » compte 25 étudiants
  Quand P1 affiche la liste des étudiants de « L3 GL »
  Alors exactement ces 25 étudiants sont listés, sans statut ni note prédéfinis

Scénario: [FEAT-003-SC-27] [CIBLE] Cas d'isolation Multi-Tenant
  Étant donné qu'un professeur authentifié appartient à l'école A
  Quand il affiche la liste des étudiants d'un cours ou d'une classe
  Alors aucun étudiant de l'école B n'apparaît
```

### Traçabilité règles → scénarios
| Règle | Scénarios |
| :--- | :--- |
| BR-01 | SC-01, SC-02, SC-03 |
| BR-02 | SC-08 |
| BR-03 | SC-09 |
| BR-04 | SC-06, SC-07, SC-10 |
| BR-05 | SC-06 |
| BR-06 | SC-13, SC-14, SC-15, SC-16 |
| BR-07, BR-08 | SC-17 |
| BR-09 | SC-11, SC-22, SC-24 |
| BR-10 | SC-11, SC-26 |
| BR-11 | SC-05, SC-12, SC-18, SC-23, SC-27 |
| BR-12 | SC-19, SC-20, SC-21 |
| BR-13 | SC-24, SC-25 |
| BR-14 | SC-06, SC-13, SC-22 |
| BR-15 | SC-04 |
| BR-16 | SC-10 |
| BR-17 | SC-26 |

---

## 6. Exigences Non-Fonctionnelles (NFR)
- **Performance** : listes paginées (cours, devoirs, leçons, modules, quiz par cours : page 0 / 10 éléments par défaut) < 500 ms. ⚠️ Non paginées aujourd'hui : notes d'un cours, emploi du temps, rappels, étudiants d'un cours / d'une classe, quiz d'un module (limités aux 10 premiers, PC:361).
- **Sécurité & Confidentialité** : notes et présences sont des données personnelles d'élèves potentiellement mineurs. Accès restreint par rôle (BR-15), au titulaire du cours (BR-09, cible) et à l'école (BR-11). Les messages d'erreur ne doivent pas révéler l'existence d'une séance d'un autre professeur au-delà du refus « interdit ».
- **Volumétrie Attendue** : estimation non sourcée, voir hypothèse H-03 (section 7).
- **Audit & Traçabilité** : saisie/modification de note, annulation, report, création de devoir / quiz, soumission de présences → trace immuable dans `audit_logs` avec auteur authentifié, école, date-heure, valeurs avant/après pour les notes (cible BR-14 ; aujourd'hui journal technique uniquement).

---

## 7. ❓ Hypothèses & Points à Confirmer

### Questions au Tech Lead
- [ ] **Q1** `[À VALIDER]` **Moyenne avec une seule note** : le calcul enregistré prend la note présente comme moyenne (CC seul 12 → 12, PRA:144-146), le calcul affiché compte la note absente pour 0 (CC seul 12 → 4,8, mention F, GD:43-46). Laquelle est la règle ? (Proposition : pas de moyenne ni de mention tant que les deux notes ne sont pas saisies.)
- [ ] **Q2** `[À VALIDER]` **Saisie partielle** : saisir seulement l'examen doit-il conserver le CC déjà saisi (BR-16) ? Aujourd'hui il est effacé.
- [ ] **Q3** `[À VALIDER]` **Périmètre du professeur** : confirmez-vous qu'un professeur ne peut agir (notes, devoirs, quiz, leçons, modules, rappels, présences) que sur ses propres cours, et sur les seuls étudiants inscrits (BR-09, BR-10) ? Les administrateurs gardent-ils la même dérogation qu'en BR-06 ?
- [ ] **Q4** `[À VALIDER]` **Verrouillage des notes** : la règle globale BR-04 du registre (« non modifiable après clôture du trimestre ») n'a aucun équivalent dans le code (pas de notion de période ni de clôture). Faut-il l'intégrer à FEAT-003 ou la reporter à une feature « bulletins » ?
- [ ] **Q5** `[À VALIDER]` **Annulation / report** : faut-il un délai minimal avant la séance, interdire l'annulation d'une séance déjà annulée, contrôler les conflits de salle, notifier les étudiants ? Et faut-il conserver deux points d'entrée en doublon (« planning » et « emploi du temps ») ou n'en garder qu'un, avec motif et créneau obligatoires ?

### Hypothèses temporaires
- [ ] `[À VALIDER]` **H-01** : la liste fermée des statuts de présence n'est pas définie dans le code (statut libre). Hypothèse : Présent / Absent / Retard / Excusé, à aligner avec FEAT-006 (justification d'absence).
- [ ] `[À VALIDER]` **H-02** : le barème de mention A–F (GD:52-58) est conservé tel quel ; il diffère des mentions usuelles (Passable, Assez bien, Bien, Très bien).
- [ ] `[À VALIDER]` **H-03** : volumétrie estimée par école et par an (aucune donnée source) : ~50 professeurs, ~500 cours, ~20 000 notes, ~200 000 relevés de présence.
- [ ] `[À VALIDER]` **H-04** : la fuite inter-écoles sur les listes d'étudiants (BR-11) est déduite de la lecture du code (lecture par rôle sans filtre d'école, entité Utilisateur sans marqueur d'école) ; non démontrée par un test. À confirmer par l'Agent 05/06.
- [ ] `[À VALIDER]` **H-05** : pour un administrateur, l'annulation d'une séance inexistante produit une erreur générique (« Session not found », PS:132) et non un refus métier « séance introuvable » ; code de retour exact non vérifié.

### Écarts techniques constatés (pour information Agent 02 — aucune décision prise ici)
- Date d'origine d'une séance reportée = instant du report (PS:146) au lieu de la date initiale.
- Quiz de module et quiz de cours partagent le même rattachement (PEC:62/82, PRA:244).
- Exemption PLATFORM_ADMIN prévue dans le contrôle (PEC:216) mais ce rôle n'a pas accès à l'espace professeur (SC:108) : exemption inopérante.

---

## 8. 📝 Historique des Révisions (Changelog)
| Date | Version | Auteur | Nature des Modifications |
| :--- | :---: | :--- | :--- |
| 2026-11-09 | v1.0 | Agent 01 | Création initiale par rétro-spécification du code réel (ProfessorController, ProfExtraController, ProfessorService, SecurityConfig) ; états RÉEL / PARTIEL / NON RÉEL ; 5 questions au Tech Lead |
