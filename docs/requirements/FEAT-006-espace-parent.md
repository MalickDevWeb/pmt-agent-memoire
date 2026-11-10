# 📋 Spécification Fonctionnelle : FEAT-006 — Espace Parent

| Métadonnée | Valeur |
| :--- | :--- |
| **Identifiant** | FEAT-006 |
| **Auteur** | Agent 01 — Product Analyst |
| **Validé par (Tech Lead)** | ⏳ En attente |
| **Statut** | DRAFT |
| **Version** | v1.0 |

---

## 1. Contexte & Valeur Métier
- **Problématique & Objectif** : Offrir aux parents un espace de suivi de la scolarité de **leurs propres enfants** (identité, notes, présences, emploi du temps, situation de paiement), de prise de rendez-vous avec les professeurs et de justification des absences. Gain pour les écoles : moins de sollicitations du secrétariat, absences justifiées plus vite, relation école-famille tracée. Condition non négociable : un parent ne voit **jamais** les données d'un enfant qui ne lui est pas lié, et ne voit **jamais** une donnée inventée présentée comme réelle (des données d'enfants mineurs et des données financières sont en jeu).
- **Acteurs Cibles** : Parent (bénéficiaire principal) ; Admin Établissement (crée les liens parent-enfant, reçoit les justifications) ; Professeur (destinataire des demandes de rendez-vous).
- **Existant de référence** : section 2.6 « Espace Parent » de `docs/api-contract.md` (statut IN_REVIEW, Gate 2 non franchie) et module parent du backend. Les écarts entre l'existant et la présente spécification sont listés en section 9 (constats, sans modification du code).

---

## 2. Périmètre (Scope)
### ✅ Dans le Périmètre (In-Scope)
- **Mes enfants** : liste des enfants liés au parent connecté, et uniquement ceux-là.
- **Notes** d'un enfant lié.
- **Présences** (présent / absent / retard) d'un enfant lié, filtrables par mois.
- **Planning** hebdomadaire (emploi du temps) d'un enfant lié.
- **Paiements de scolarité** : affichage explicite « non disponible » tant qu'aucune source réelle n'existe.
- **Rendez-vous** : demande d'un rendez-vous avec un professeur et consultation de **ses propres** rendez-vous.
- **Justification d'absence** d'un enfant lié.
- Règles transverses : rôle Parent obligatoire, contrôle de filiation (refus 403), isolation par établissement, interdiction des données inventées.

### ❌ Hors Périmètre (Out-of-Scope)
- Création, modification ou suppression des liens parent-enfant (relève de l'Admin Établissement — à spécifier avec FEAT-002, actuellement manquante).
- Messagerie parent ↔ école, dossiers de candidature / inscription d'un nouvel enfant, modification du profil parent, tableau de bord statistique de l'enfant : non demandés dans cette itération (voir constats §9, ces fonctions servent aujourd'hui des données fictives ou non enregistrées).
- Paiement en ligne de la scolarité (Wave, Orange Money, carte…) : seule la consultation est visée, et elle est « non disponible » à ce stade.
- Circuit de validation des justifications par l'administration (acceptation / refus) : dépend de la question Q2.
- Visioconférence associée aux rendez-vous.
- Notifications (SMS, e-mail, push) aux parents.

---

## 3. Dictionnaire de Données Métier
*Définition conceptuelle des entités manipulées (aucun terme technique de stockage).*

| Entité Métier | Attribut Métier | Type / Format Naturel | Obligatoire ? | Description & Contraintes Métier |
| :--- | :--- | :--- | :---: | :--- |
| **Parent** | Identité | Identifiant interne | Oui | Toujours déduite du compte connecté ; jamais saisie ni transmise par le parent. |
| **Parent** | Établissement | Référence établissement | Oui | Établissement de rattachement du compte parent. |
| **Lien Parent-Enfant** | Parent | Référence Parent | Oui | Parent autorisé à suivre l'enfant. |
| **Lien Parent-Enfant** | Enfant | Référence Étudiant | Oui | Enfant suivi. Seule source qui autorise l'accès d'un parent aux données d'un enfant. |
| **Lien Parent-Enfant** | Établissement | Référence établissement | Oui | Doit être le même établissement que le parent et l'enfant. |
| **Enfant (vue parent)** | Nom, Prénom | Texte | Non | Issus du compte réel de l'élève ; « non renseigné » si absents. |
| **Enfant (vue parent)** | Matricule | Texte | Non | Issu du compte réel ; « non renseigné » si absent. |
| **Enfant (vue parent)** | Filière, Niveau, Classe, Photo | Texte / Image | Non | Affichés uniquement s'ils proviennent d'une source réelle ; sinon « non renseigné ». |
| **Note** | Module | Texte | Oui | Matière évaluée. |
| **Note** | Professeur | Texte | Oui | Enseignant du module. |
| **Note** | Contrôle continu, Examen, Moyenne | Décimal de 0 à 20 | Non | Bornes conformes à la règle générale BR-04 du registre. |
| **Note** | Mention | Liste : Excellent, Bien, Assez Bien, Passable, Insuffisant | Non | Dérivée de la moyenne (barème à fournir, voir Q5). |
| **Note** | Crédits ECTS | Entier positif | Non | Crédits du module. |
| **Présence** | Date, Heure, Cours, Professeur | Date / Créneau / Texte | Oui | Séance concernée. |
| **Présence** | Statut | Liste : Présent, Absent, Retard | Oui | État relevé pour l'enfant. |
| **Créneau de planning** | Jour, Horaire, Cours, Professeur, Salle | Jour de la semaine / Plage horaire / Texte | Oui | Séance prévue pour l'enfant. |
| **Créneau de planning** | Type | Liste : Cours magistral, Travaux dirigés, Travaux pratiques | Oui | Nature de la séance. |
| **Situation de paiement** | Disponibilité | Liste : Disponible, Non disponible | Oui | « Non disponible » tant qu'aucune source réelle n'est raccordée. |
| **Situation de paiement** | Total annuel | Montant entier en francs CFA | Non | Renseigné uniquement si disponible. |
| **Échéance** | Libellé, Montant, Date limite, Statut, Date de paiement | Texte / Montant / Date / Liste : Payé, En cours, En retard / Date | Non | Renseignée uniquement si disponible. |
| **Rendez-vous** | Parent | Référence Parent | Oui | Toujours le parent connecté. |
| **Rendez-vous** | Professeur | Référence Professeur | Oui | Professeur réel de l'établissement du parent. |
| **Rendez-vous** | Nom du professeur | Texte | Oui | Issu du compte réel du professeur, jamais d'un nom par défaut. |
| **Rendez-vous** | Date souhaitée | Date et heure | Oui | Date proposée par le parent. |
| **Rendez-vous** | Motif | Texte | Oui | Objet de la demande. |
| **Rendez-vous** | Statut | Liste (valeurs à confirmer, Q3) | Oui | État de la demande. |
| **Justification d'absence** | Présence concernée | Référence Présence | Oui | Doit concerner un enfant lié au parent connecté et une absence. |
| **Justification d'absence** | Motif | Texte non vide | Oui | Explication fournie par le parent. |
| **Justification d'absence** | Pièce justificative | Document | Non | Certificat médical, etc. (caractère obligatoire à confirmer, Q2). |
| **Justification d'absence** | Date de dépôt | Date et heure | Oui | Horodatage du dépôt. |

---

## 4. Matrice des Règles Métier (Business Rules)
*Échelle de sévérité imposée : BLOQUANT | MAJEUR | MINEUR.*

| Réf Règle | Intitulé | Description Stricte | Sévérité |
| :--- | :--- | :--- | :---: |
| **FEAT-006-BR-01** | Rôle Parent obligatoire | Toutes les fonctions de l'espace parent exigent un compte authentifié de rôle Parent. Sans authentification : refus 401. Compte d'un autre rôle (y compris Admin, Professeur, Étudiant) : refus 403. | BLOQUANT |
| **FEAT-006-BR-02** | Identité déduite du compte connecté | Le parent concerné par une opération est toujours le titulaire du compte connecté. Aucun identifiant de parent fourni par l'utilisateur n'est pris en compte. | BLOQUANT |
| **FEAT-006-BR-03** | Filiation obligatoire (lien parent-enfant) | Un parent n'accède qu'aux données (identité, notes, présences, planning, justifications) des enfants qui lui sont liés dans le registre des liens parent-enfant. Toute demande portant sur un autre enfant est refusée avec un refus 403, sans aucune donnée de l'enfant dans la réponse. | BLOQUANT |
| **FEAT-006-BR-04** | Isolation par établissement | Le parent, l'enfant, le lien qui les unit, les professeurs proposés et les rendez-vous appartiennent au même établissement. Un lien ou un enfant d'un autre établissement est traité comme non lié (refus 403). | BLOQUANT |
| **FEAT-006-BR-05** | Jamais de donnée inventée | Aucune valeur fictive, par défaut ou de démonstration (élève, note, présence, créneau, professeur, rendez-vous, montant) n'est présentée au parent. En l'absence de source réelle, la rubrique affiche explicitement « non disponible » ; une donnée absente d'un enregistrement réel s'affiche « non renseigné ». | BLOQUANT |
| **FEAT-006-BR-06** | Liste des enfants exacte | La liste « Mes enfants » contient exactement les enfants liés au parent connecté. Sans lien, elle est vide et accompagnée d'un message invitant à contacter l'établissement ; aucun enfant n'est ajouté par défaut. | BLOQUANT |
| **FEAT-006-BR-07** | Paiements non disponibles | Tant qu'aucune source réelle de paiements n'existe, la rubrique Paiements affiche « non disponible ». Un total à zéro et une liste d'échéances vide ne doivent jamais être présentés comme « rien à payer » ou « à jour ». | BLOQUANT |
| **FEAT-006-BR-08** | Rendez-vous personnels | Un parent ne voit que les rendez-vous qu'il a lui-même demandés. Sans rendez-vous, la liste est vide ; aucun rendez-vous d'un autre parent ni rendez-vous créé automatiquement n'est affiché. | BLOQUANT |
| **FEAT-006-BR-09** | Demande de rendez-vous valide | Une demande de rendez-vous vise un professeur réel et actif de l'établissement du parent, avec une date souhaitée et un motif renseignés. Sinon, refus explicite et aucune demande enregistrée. | MAJEUR |
| **FEAT-006-BR-10** | Justification limitée aux enfants liés | Une justification n'est acceptée que pour une absence d'un enfant lié au parent connecté (refus 403 sinon). Une présence inexistante entraîne un refus explicite. | BLOQUANT |
| **FEAT-006-BR-11** | Justification complète et enregistrée | Le motif est obligatoire et non vide. Une confirmation n'est affichée au parent que si la justification a réellement été enregistrée ; elle reste ensuite consultable par le parent et par l'établissement. | MAJEUR |
| **FEAT-006-BR-12** | Traçabilité | Les dépôts de justification, les demandes de rendez-vous et les refus d'accès pour défaut de filiation génèrent une entrée immuable dans le journal d'audit (`audit_logs`). | MAJEUR |

---

## 5. User Stories & Scénarios d'Acceptation (Gherkin en Français)

### User Story [FEAT-006-US-01] : Consulter la liste de mes enfants
> **En tant que** Parent  
> **Je veux** voir la liste de mes enfants inscrits dans l'établissement  
> **Afin de** choisir l'enfant dont je suis la scolarité  
> **Règles associées** : `FEAT-006-BR-01`, `FEAT-006-BR-02`, `FEAT-006-BR-04`, `FEAT-006-BR-05`, `FEAT-006-BR-06`

#### Scénarios d'Acceptation :

Scénario: [FEAT-006-SC-01] Cas nominal — Liste des enfants liés
  Étant donné que le parent « Mamadou Diallo » est connecté
  Et que deux enfants lui sont liés dans le registre des liens parent-enfant de son établissement
  Quand il ouvre la rubrique « Mes enfants »
  Alors exactement ces deux enfants sont affichés avec leurs nom, prénom et matricule réels
  Et aucun autre élève de l'établissement n'apparaît

Scénario: [FEAT-006-SC-02] Cas limite — Aucun enfant lié
  Étant donné que le parent connecté n'a aucun lien parent-enfant enregistré
  Quand il ouvre la rubrique « Mes enfants »
  Alors la liste est vide
  Et un message l'invite à contacter l'établissement pour rattacher ses enfants
  Et aucun enfant par défaut ou de démonstration n'est proposé

Scénario: [FEAT-006-SC-03] Cas limite — Informations scolaires absentes
  Étant donné qu'un enfant lié n'a ni filière, ni niveau, ni classe connus de façon fiable
  Quand le parent consulte la fiche de cet enfant
  Alors ces informations sont affichées « non renseigné »
  Et aucune valeur n'est déduite ou inventée

Scénario: [FEAT-006-SC-04] Cas d'erreur — Compte d'un autre rôle
  Étant donné qu'un utilisateur connecté a le rôle Étudiant ou Professeur
  Quand il tente d'accéder à l'espace parent
  Alors l'accès est refusé avec un refus 403
  Et aucune donnée d'enfant n'est renvoyée

Scénario: [FEAT-006-SC-05] Cas d'isolation Multi-Tenant — Identité imposée par le compte
  Étant donné que le parent A de l'école A est connecté
  Quand il tente de consulter la liste des enfants en désignant le parent B ou un parent de l'école B
  Alors seule sa propre liste d'enfants, rattachés à l'école A, lui est présentée
  Et aucun enfant du parent B ni de l'école B n'apparaît

---

### User Story [FEAT-006-US-02] : Consulter les notes d'un enfant
> **En tant que** Parent  
> **Je veux** consulter les notes et moyennes de mon enfant  
> **Afin de** suivre ses résultats et réagir à temps  
> **Règles associées** : `FEAT-006-BR-03`, `FEAT-006-BR-04`, `FEAT-006-BR-05`, `FEAT-006-BR-12`

#### Scénarios d'Acceptation :

Scénario: [FEAT-006-SC-06] Cas nominal — Notes réelles d'un enfant lié
  Étant donné que l'enfant « Awa » est lié au parent connecté
  Et que des notes ont été réellement saisies pour elle
  Quand le parent consulte ses notes
  Alors chaque module affiche le contrôle continu, l'examen, la moyenne et les crédits enregistrés
  Et toutes les valeurs sont comprises entre 0 et 20

Scénario: [FEAT-006-SC-07] Cas limite — Aucune source réelle de notes
  Étant donné que l'enfant est lié au parent connecté
  Et qu'aucune note réelle n'est disponible pour cet enfant
  Quand le parent consulte ses notes
  Alors la rubrique affiche « Notes non disponibles »
  Et aucune note de démonstration n'est affichée

Scénario: [FEAT-006-SC-08] Cas d'erreur métier — Enfant d'une autre famille
  Étant donné que l'élève « Moussa » n'est pas lié au parent connecté
  Quand le parent tente de consulter les notes de Moussa
  Alors l'accès est refusé avec un refus 403
  Et aucune note ni information sur Moussa n'est renvoyée
  Et le refus est consigné dans le journal d'audit

Scénario: [FEAT-006-SC-09] Cas d'isolation Multi-Tenant
  Étant donné qu'un parent authentifié appartient à l'école A
  Quand il tente de consulter les notes d'un élève de l'école B
  Alors l'accès est strictement rejeté avec un refus 403

---

### User Story [FEAT-006-US-03] : Consulter les présences d'un enfant
> **En tant que** Parent  
> **Je veux** voir les présences, absences et retards de mon enfant, mois par mois  
> **Afin de** détecter l'absentéisme et justifier les absences  
> **Règles associées** : `FEAT-006-BR-03`, `FEAT-006-BR-04`, `FEAT-006-BR-05`

#### Scénarios d'Acceptation :

Scénario: [FEAT-006-SC-10] Cas nominal — Présences du mois choisi
  Étant donné que l'enfant est lié au parent connecté
  Et que des présences réelles existent pour lui en octobre 2026
  Quand le parent consulte les présences du mois d'octobre 2026
  Alors seules les séances d'octobre 2026 sont affichées avec leur statut Présent, Absent ou Retard
  Et chaque absence indique si elle est déjà justifiée

Scénario: [FEAT-006-SC-11] Cas limite — Aucune source réelle de présences
  Étant donné que l'enfant est lié au parent connecté
  Et qu'aucune présence réelle n'est disponible
  Quand le parent consulte les présences
  Alors la rubrique affiche « Présences non disponibles »
  Et aucune présence de démonstration n'est affichée

Scénario: [FEAT-006-SC-12] Cas d'isolation — Enfant non lié ou d'une autre école
  Étant donné qu'un parent de l'école A n'est pas lié à l'élève demandé, inscrit dans l'école A ou l'école B
  Quand il tente de consulter les présences de cet élève
  Alors l'accès est refusé avec un refus 403
  Et aucune donnée de présence n'est renvoyée

---

### User Story [FEAT-006-US-04] : Consulter le planning d'un enfant
> **En tant que** Parent  
> **Je veux** voir l'emploi du temps hebdomadaire de mon enfant  
> **Afin d'** organiser la vie familiale autour de ses cours  
> **Règles associées** : `FEAT-006-BR-03`, `FEAT-006-BR-04`, `FEAT-006-BR-05`

#### Scénarios d'Acceptation :

Scénario: [FEAT-006-SC-13] Cas nominal — Emploi du temps réel
  Étant donné que l'enfant est lié au parent connecté
  Et qu'un emploi du temps réel est publié pour sa classe
  Quand le parent consulte le planning
  Alors les créneaux de la semaine sont affichés avec jour, horaire, cours, professeur, salle et type

Scénario: [FEAT-006-SC-14] Cas limite — Aucun planning réel
  Étant donné que l'enfant est lié au parent connecté
  Et qu'aucun emploi du temps réel n'est disponible
  Quand le parent consulte le planning
  Alors la rubrique affiche « Planning non disponible »
  Et aucun créneau de démonstration n'est affiché

Scénario: [FEAT-006-SC-15] Cas d'isolation — Enfant non lié
  Étant donné que l'élève demandé n'est pas lié au parent connecté
  Quand le parent tente de consulter son planning
  Alors l'accès est refusé avec un refus 403

---

### User Story [FEAT-006-US-05] : Consulter la situation de paiement
> **En tant que** Parent  
> **Je veux** consulter les échéances de scolarité de mes enfants  
> **Afin de** savoir ce qui est payé, en cours ou en retard  
> **Règles associées** : `FEAT-006-BR-01`, `FEAT-006-BR-03`, `FEAT-006-BR-05`, `FEAT-006-BR-07`

#### Scénarios d'Acceptation :

Scénario: [FEAT-006-SC-16] Cas nominal actuel — Paiements non disponibles
  Étant donné que le parent est connecté
  Et qu'aucune source réelle de paiements n'est raccordée
  Quand il ouvre la rubrique « Paiements »
  Alors la rubrique affiche « Informations de paiement non disponibles »
  Et aucun montant, aucune échéance et aucune mention « à jour » ou « rien à payer » n'est affiché

Scénario: [FEAT-006-SC-17] Cas futur — Source réelle disponible
  Étant donné qu'une source réelle de paiements est raccordée
  Quand le parent ouvre la rubrique « Paiements »
  Alors seules les échéances de ses enfants liés sont affichées avec libellé, montant, date limite et statut
  Et aucune échéance d'un enfant non lié n'apparaît

Scénario: [FEAT-006-SC-18] Cas d'erreur — Compte d'un autre rôle
  Étant donné qu'un utilisateur connecté n'a pas le rôle Parent
  Quand il tente d'ouvrir la rubrique « Paiements » de l'espace parent
  Alors l'accès est refusé avec un refus 403

---

### User Story [FEAT-006-US-06] : Demander et suivre mes rendez-vous
> **En tant que** Parent  
> **Je veux** demander un rendez-vous à un professeur et suivre mes demandes  
> **Afin d'** échanger avec l'équipe pédagogique sur la scolarité de mon enfant  
> **Règles associées** : `FEAT-006-BR-02`, `FEAT-006-BR-04`, `FEAT-006-BR-05`, `FEAT-006-BR-08`, `FEAT-006-BR-09`, `FEAT-006-BR-12`

#### Scénarios d'Acceptation :

Scénario: [FEAT-006-SC-19] Cas nominal — Demande de rendez-vous
  Étant donné que le parent est connecté
  Et qu'il choisit un professeur réel et actif de son établissement, une date souhaitée et un motif
  Quand il envoie la demande
  Alors la demande est enregistrée au nom du parent connecté avec le nom réel du professeur
  Et elle apparaît dans sa liste de rendez-vous
  Et la demande est consignée dans le journal d'audit

Scénario: [FEAT-006-SC-20] Cas nominal — Liste limitée à mes rendez-vous
  Étant donné que le parent A a demandé deux rendez-vous
  Et que le parent B a demandé trois rendez-vous
  Quand le parent A consulte ses rendez-vous
  Alors seuls ses deux rendez-vous sont affichés

Scénario: [FEAT-006-SC-21] Cas limite — Aucun rendez-vous
  Étant donné que le parent connecté n'a jamais demandé de rendez-vous
  Quand il consulte ses rendez-vous
  Alors la liste est vide
  Et aucun rendez-vous d'un autre parent ni rendez-vous créé automatiquement n'est affiché

Scénario: [FEAT-006-SC-22] Cas d'erreur métier — Demande incomplète ou professeur inconnu
  Étant donné que le parent est connecté
  Et que la demande ne désigne aucun professeur réel, ou que la date souhaitée ou le motif manque
  Quand il envoie la demande
  Alors la demande est refusée avec un message indiquant l'information manquante ou invalide
  Et aucun rendez-vous n'est enregistré

Scénario: [FEAT-006-SC-23] Cas d'isolation Multi-Tenant
  Étant donné qu'un parent authentifié appartient à l'école A
  Quand il consulte la liste des professeurs ou demande un rendez-vous avec un professeur de l'école B
  Alors seuls des professeurs de l'école A lui sont proposés
  Et la demande visant un professeur de l'école B est rejetée sans être enregistrée

---

### User Story [FEAT-006-US-07] : Justifier une absence de mon enfant
> **En tant que** Parent  
> **Je veux** déposer un motif, et le cas échéant une pièce, pour justifier une absence de mon enfant  
> **Afin de** régulariser sa situation auprès de l'établissement  
> **Règles associées** : `FEAT-006-BR-03`, `FEAT-006-BR-04`, `FEAT-006-BR-10`, `FEAT-006-BR-11`, `FEAT-006-BR-12`

#### Scénarios d'Acceptation :

Scénario: [FEAT-006-SC-24] Cas nominal — Justification enregistrée
  Étant donné que l'enfant est lié au parent connecté
  Et qu'il a une absence non justifiée le 3 novembre 2026
  Et que le parent saisit le motif « Consultation médicale »
  Quand il envoie la justification
  Alors la justification est enregistrée et rattachée à cette absence
  Et une confirmation est affichée au parent seulement après cet enregistrement
  Et l'absence apparaît comme « justification déposée » dans les présences de l'enfant
  Et le dépôt est consigné dans le journal d'audit

Scénario: [FEAT-006-SC-25] Cas d'erreur métier — Motif absent
  Étant donné que l'enfant est lié au parent connecté
  Et que le parent laisse le motif vide
  Quand il envoie la justification
  Alors la justification est refusée avec le message « Le motif est obligatoire »
  Et rien n'est enregistré

Scénario: [FEAT-006-SC-26] Cas d'erreur métier — Présence inexistante
  Étant donné que la présence désignée n'existe pas
  Quand le parent envoie une justification pour celle-ci
  Alors la justification est refusée avec un message explicite
  Et aucune confirmation ni identifiant de justificatif n'est délivré

Scénario: [FEAT-006-SC-27] Cas d'isolation — Absence d'un enfant non lié
  Étant donné que l'absence désignée concerne un élève non lié au parent connecté, de l'école A ou de l'école B
  Quand le parent tente de la justifier
  Alors l'envoi est refusé avec un refus 403
  Et aucune justification n'est enregistrée
  Et le refus est consigné dans le journal d'audit

---

## 6. Exigences Non-Fonctionnelles (NFR)
- **Performance** : Affichage de chaque rubrique perçu en moins de 500 ms ; pagination par défaut pour les listes susceptibles de croître (présences, rendez-vous, justifications), avec filtre par mois pour les présences.
- **Sécurité & Confidentialité** : Données personnelles d'élèves, souvent mineurs, et données financières. Le contrôle de filiation et d'établissement s'applique à chaque demande, côté serveur, sans dépendre de l'interface. Un refus pour défaut de filiation ne révèle aucune information sur l'élève demandé. Les pièces justificatives (potentiellement médicales) ne sont visibles que par le parent déposant et le personnel habilité de l'établissement.
- **Volumétrie Attendue** : Ordre de grandeur à confirmer par le Tech Lead (cf. capacité initiale de 50 établissements, FEAT-001). Par établissement et par an, à titre indicatif : quelques centaines à quelques milliers de parents, quelques dizaines de milliers de relevés de présence consultables, quelques milliers de justifications et de demandes de rendez-vous.
- **Audit & Traçabilité** : Entrée immuable dans `audit_logs` pour : dépôt de justification, demande de rendez-vous, refus d'accès pour défaut de filiation ou d'établissement (parent, enfant demandé, date, résultat).
- **Honnêteté des données** : Chaque rubrique distingue trois états visibles : données réelles, « non renseigné » (champ absent d'un enregistrement réel), « non disponible » (aucune source réelle).

---

## 7. ❓ Hypothèses & Points à Confirmer
- [ ] `[À VALIDER]` **H1 — Même refus pour « enfant inexistant » et « enfant d'une autre famille »** : refus 403 identique dans les deux cas. *Justification* : éviter qu'un parent puisse vérifier l'existence d'un élève (énumération). Conforme au comportement constaté (`ParentController.java:64-67`).
- [ ] `[À VALIDER]` **H2 — Refus de filiation journalisés** (BR-12). *Justification* : une tentative répétée d'accès à l'enfant d'autrui est un signal de sécurité ; la règle générale BR-05 du registre ne couvre que les écritures.
- [ ] `[À VALIDER]` **H3 — Notes, présences et planning passent en « non disponible »** tant que leurs sources réelles ne sont pas raccordées. *Justification* : application directe de la consigne « jamais de donnée inventée » ; aujourd'hui ces rubriques renvoient des valeurs fixes (cf. §9).
- [ ] `[À VALIDER]` **H4 — Un lien parent-enfant reste valable si l'enfant est majeur** (enseignement supérieur). *Justification* : aucune règle de fin d'accès n'est exprimée ; à arbitrer pour la protection des données d'un étudiant majeur.
- [ ] `[À VALIDER]` **H5 — La justification ne concerne que les absences**, pas les retards. *Justification* : le brief parle de « justification d'absence » ; l'existant accepte « absence/retard » (`ParentController.java:271`).

---

## 8. ❓ Questions au Tech Lead
1. **Q1 — Rattachement du lien parent-enfant** : le lien doit-il être rattaché au **compte de connexion** du parent ou à sa **fiche Parent** ? Constat : l'identité utilisée pour le contrôle est celle du compte (`ParentController.java:302`), alors que le lien d'amorçage est rattaché à la fiche (`DataInitializer.java:472-473` fiche `parent-001` ↔ compte `usr-parent-01` ; `DataInitializer.java:483` lien sur `parent-001`). *Hypothèse non vérifiée par exécution* : le parent de démonstration verrait une liste d'enfants vide.
2. **Q2 — Circuit de la justification** : qui la valide (Admin, Professeur principal) ? Statuts attendus (déposée / acceptée / refusée) ? Délai maximal de dépôt après l'absence ? Pièce justificative obligatoire ? Une justification peut-elle être modifiée ou retirée ?
3. **Q3 — Périmètre des rendez-vous** : un parent peut-il solliciter **tout** professeur de l'établissement, ou seulement ceux qui enseignent à ses enfants ? La demande doit-elle désigner l'enfant concerné ? Qui confirme / refuse et avec quels statuts ?
4. **Q4 — Source et granularité des paiements** : quelle source réelle (module Finance, échéanciers) alimentera la rubrique, et quand ? Les échéances sont-elles par enfant ou par famille ? Si deux parents sont liés au même enfant, voient-ils tous deux les paiements ?
5. **Q5 — Visibilité des notes** : une note est-elle visible par le parent dès sa saisie, ou seulement après publication / clôture de la période ? Quel barème de mentions appliquer ?

---

## 9. 🔎 Constats sur l'existant (données de contexte, aucune modification de code)
*Faits relevés au 2026-11-09 par lecture des fichiers cités ; à traiter par l'Architecte / le Backend après approbation.*

| # | Constat | Preuve | Règle concernée |
| :--- | :--- | :--- | :--- |
| C1 | Contrôle de filiation présent sur les 4 consultations par enfant (stats, présences, notes, planning) : refus 403 si l'enfant n'est pas lié. | `ParentController.java:64-67, 85-88, 105-108, 125-128` | BR-03 (conforme) |
| C2 | La liste des enfants ne renvoie que les liens enregistrés ; filière/niveau/classe/photo toujours vides. | `ParentService.java:58-70` | BR-05, BR-06 (conforme) |
| C3 | **Justification d'absence sans contrôle de filiation et non enregistrée** : un identifiant de justificatif est fabriqué même pour une présence inexistante ou d'un autre enfant. | `ParentController.java:270-281` ; `ParentService.java:316-324` | BR-10, BR-11 (**non conforme**) |
| C4 | Notes, présences, planning, stats servent des valeurs fixes de démonstration (le filtre mois est ignoré). | `docs/api-contract.md:300-303` (carte APP-BE-19) | BR-05 (**non conforme**) |
| C5 | Liste des professeurs : 2 professeurs fictifs renvoyés si aucun compte Professeur ; filtrage par établissement non visible dans le contrôleur (hypothèse à vérifier dans le dépôt des utilisateurs). | `ParentController.java:251, 261-264` | BR-04, BR-05 (**à corriger / vérifier**) |
| C6 | Demande de RDV : nom du professeur remplacé par « Dr. Sall (Algorithmique & IA) » si l'identifiant ne contient pas « — » ; aucun contrôle d'existence du professeur. | `ParentService.java:278-280` | BR-05, BR-09 (**non conforme**) |
| C7 | Liste des RDV désormais limitée au parent connecté, sans repli ni RDV d'amorçage (APP-SEC-14). **Le contrat `docs/api-contract.md` §2.6 est en retard** : il décrit encore le repli sur tous les RDV. | `ParentService.java:294-314` vs `docs/api-contract.md:272, 312` | BR-08 (code conforme, contrat à mettre à jour) |
| C8 | Paiements : réponse « non_disponible » sans donnée fictive. | `ParentService.java:253-262` ; `docs/api-contract.md:240-251` | BR-07 (conforme) |
| C9 | Recherche des liens parent-enfant par parent seul, sans critère d'établissement explicite (alors que l'établissement est porté par le lien). | `ParentEnfantJpaRepository.java:9, 11` ; `ParentEnfantJpaEntity.java:10-11` | BR-04 (à évaluer par l'Architecte) |

---

## 10. 📝 Historique des Révisions (Changelog)
| Date | Version | Auteur | Nature des Modifications |
| :--- | :---: | :--- | :--- |
| 2026-11-09 | v1.0 | Agent 01 | Création initiale (DRAFT) : 7 US, 27 scénarios, 12 règles, 5 hypothèses, 5 questions, 9 constats sur l'existant |
