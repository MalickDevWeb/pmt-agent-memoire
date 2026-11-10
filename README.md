# 🤖 Guide Complet & Manuel de Réutilisation : Le Framework d'Ingénierie Agentique Supervisée (Kasongo Framework)

> **Auteur :** Ndèye Fatou Fall (Agent 09) & Équipe École 221  
> **Version du Framework :** 2.0.0 (Architecture Multi-Agents avec Supervision Formelle & Human-in-the-Loop)  
> **Objet :** Documentation intégrale du framework multi-agents développé pour l'ERP École 221, et guide d'extraction sous forme de **Starter Kit / Package GitHub Template / Gist réutilisable** pour toute application future (SaaS, Mobile, API, FinTech, Santé, etc.).

---

## 📑 Table des Matières

1. [Vision & Philosophie du Framework](#1-vision--philosophie-du-framework)
2. [Architecture du Framework & Arborescence Portable](#2-architecture-du-framework--arborescence-portable)
3. [Les 12 Profils d'Agents Spécialisés](#3-les-12-profils-dagents-spécialisés)
4. [Le Bus de Communication Asynchrone (`agent_messages.md`)](#4-le-bus-de-communication-asynchrone-agent_messagesmd)
5. [Le Moteur de Contrôle Automatisé (Kasongo & Quality Gates)](#5-le-moteur-de-contrôle-automatisé-kasongo--quality-gates)
6. [L'Orchestrateur Unifié (`orchestrator.sh`)](#6-lorchestrateur-unifié-orchestratorsh)
7. [Guide d'Exportation : Comment packager et réutiliser le Framework sur un autre projet](#7-guide-dexportation--comment-packager-et-réutiliser-le-framework-sur-un-autre-projet)
8. [Conclusion & Bénéfice Académique / Professionnel](#8-conclusion--bénéfice-académique--professionnel)

---

## 1. Vision & Philosophie du Framework

L'ingénierie logicielle assistée par IA souffre souvent de deux dérives majeures :
1. **L'usage non maîtrisé ("Vibe Coding")** : du code généré en vrac sans contrat d'interface, introduisant des données fictives, des failles de sécurité invisibles ou des régressions massives.
2. **L'illusion d'autonomie complète** : l'absence d'arbitrage humain mène à des dérives fonctionnelles et à une perte de maîtrise intellectuelle du système par les développeurs.

Le **Framework Agentique Supervisé** résout ces écueils en instaurant une organisation inspirée des meilleures pratiques d'ingénierie d'entreprise :
- **Spécialisation des rôles** : chaque agent possède un périmètre strict et des interdictions formelles qu'il ne peut violer.
- **Portes de qualité infranchissables (*Quality Gates*)** : chaque phase (Besoins, Contrats, Code, Tests, Sécurité) doit être validée par une preuve machine avant d'autoriser la suivante.
- **Principe du Cliquet Anti-Régression** : la dette technique (types `any`, tests non passants) ne peut que diminuer, jamais régresser.
- **Validation humaine souveraine (*Human-in-the-Loop*)** : le Tech Lead humain reste le seul décideur habilité à valider les revues de code, effectuer les fusions Git (`merge`) et autoriser les déploiements.

```
       ┌────────────────────────────────────────────────────────┐
       │             👤 TECH LEAD HUMAIN (Arbitre)             │
       └──────────────────────────┬─────────────────────────────┘
                                  │ (Visa souverain Gate 5)
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │         👮 Agent 00 : Kasongo (Superviseur)            │
       │    (check_handover.py, check_agent_rules.py)           │
       └──────────────────────────┬─────────────────────────────┘
                                  │ (Contrôle mécanique)
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │    📬 Bus Asynchrone Global (agent_messages.md)         │
       └──────────────┬──────────────────────────┬──────────────┘
                      │                          │
        ┌─────────────┴──────────┐ ┌─────────────┴──────────┐
        │ Conception & Archi     │ │ Développement & Tests  │
        │ • Agent 01 (Analyste)  │ │ • Agent 03 (Backend)   │
        │ • Agent 02 (Architecte)│ │ • Agent 04 (Frontend)  │
        │ • Agent 11 (UML)       │ │ • Agent 05 (QA)        │
        └────────────────────────┘ │ • Agent 07 (DevSecOps) │
                                   │ • Agent 06 (Reviewer)  │
                                   └────────────────────────┘
```

---

## 2. Architecture du Framework & Arborescence Portable

Voici la structure exacte des fichiers composant le framework. Cette arborescence est conçue pour être **100 % isolable** et transposable dans n'importe quel dépôt logiciel.

```text
├── agents/                           # 📁 Fiches de poste et contrats des 12 agents
│   ├── 00_supervisor.md              # Kasongo — Superviseur et garant de la gouvernance
│   ├── 01_product_analyst.md         # Mame Diarra — Analyse métier, User Stories (US)
│   ├── 02_software_architect.md      # Cheikh Tidiane Diop — Architecte, Contrat OpenAPI
│   ├── 03_backend_developer.md       # Ousmane Marra — Développeur Backend (Spring Boot/Java)
│   ├── 04_frontend_developer.md      # Abdoulaye — Développeur Frontend (React/TS/Zod)
│   ├── 05_qa_engineer.md             # Aïssatou Ba — Ingénieur QA (Suites d'intégration)
│   ├── 06_code_reviewer.md           # Moussa Diallo — Auditeur statique de code & anti-mocks
│   ├── 07_devsecops_engineer.md      # Fallou Ndiaye — Sécurité, CVE, Docker, Secrets
│   ├── 08_business_marketing.md      # Khady Sarr — Modélisation économique, CAPEX/OPEX
│   ├── 09_technical_writer.md        # Ndèye Fatou Fall — Documentation & Mémoire académique
│   ├── 10_release_engineer.md        # Ibrahima Guèye — Releases SemVer, CI/CD, Déploiement
│   └── 11_modeling_engineer.md       # Seynabou Cissé — Modélisation UML & C4
│
├── audit/                            # 📁 Garde-fous et outils d'audit automatisés
│   ├── check_handover.py             # Vérifie le périmètre, les secrets et le bus avant remise
│   ├── check_agent_rules.py          # Contrôle les règles bloquantes et cliquets anti-dette
│   ├── kasongo_report.py             # Évalue la Definition of Done et génère le rapport SUP
│   ├── agent_rules_baseline.json     # Valeurs de référence (seuils de cliquets R1 à R11)
│   └── collect_evidence.sh           # Capture automatique des preuves de tests et de build
│
├── orchestration/                    # 📁 Moteur d'exécution des agents autonomes
│   ├── agent_runtime.py              # Exécute un agent avec budget de jetons plafonné
│   └── convocation.py                # Gestion des convocations en cas de travail à reprendre
│
├── docs/supervision/                 # 📁 Rapports de conformité émis par le Superviseur
│   └── SUP-*.md                      # Feuilles d'audit horodatées avec verdicts
│
├── agent_messages.md                 # 📬 Bus de communication asynchrone central
└── orchestrator.sh                   # 🛠️ CLI maître pilotant l'ensemble du pipeline
```

---

## 3. Les 12 Profils d'Agents Spécialisés

Chaque agent est régi par un fichier Markdown dans `agents/` structuré selon le schéma :
1. **Rôle & Responsabilité**
2. **Ce qu'il n'a PAS le droit de faire** (Interdictions formelles bloquantes)
3. **Contexte d'entrée** (Artéfacts consommés)
4. **Livrables attendus** (Fichiers autorisés en écriture)
5. **Règles vérifiables par machine** (Règles bloquantes vs Cibles à cliquet)

### Résumé des 12 fiches :
- **Agent 00 — Kasongo (Superviseur)** : Autorité de conformité mécanique. Bloque toute tentative de modification hors périmètre, injection de mot de passe ou régression.
- **Agent 01 — Product Analyst** : Écrit `docs/requirements.md` avec des scénarios Gherkin testables. Interdiction de modifier le code.
- **Agent 02 — Software Architect** : Garanti l'architecture hexagonale et le contrat REST unique `docs/api-contract.md`. Zéro endpoint non spécifié.
- **Agent 03 — Backend Developer** : Implémente le domaine pur et les adaptateurs Spring Boot. Interdiction formelle de créer de fausses données en dur ou d'accorder des accès ouverts.
- **Agent 04 — Frontend Developer** : Construit l'UI React avec typage strict. **Interdiction absolue d'envoyer l'en-tête `X-Tenant-Id`** depuis le client et interdiction d'augmenter le nombre de `any`.
- **Agent 05 — QA Engineer** : Élabore les scénarios de test d'intégration avec `lib_http_assert.sh`. Interdiction d'annoncer un test vert sans journal d'exécution.
- **Agent 06 — Code Reviewer** : Épluche les pull requests, traque les mocks cachés et vérifie le respect de la convention d'architecture.
- **Agent 07 — DevSecOps** : Audite les dépendances (`npm audit`, `trivy`), sécurise Docker, valide le durcissement réseau et gère `.gitleaksignore`.
- **Agent 08 — Business & Marketing** : Modélise le chiffrage d'infrastructure Cloud et le modèle d'abonnements SaaS.
- **Agent 09 — Rédacteur Technique** : Rédige le mémoire académique en LaTeX, les guides d'exploitation et documente le journal de transparence IA.
- **Agent 10 — Release & CI/CD** : Gère le versionnage sémantique, les notes de version et les workflows GitHub Actions.
- **Agent 11 — Modélisation** : Génère et vérifie l'alignement des diagrammes PlantUML avec le code réel via `gen_diagrams.py`.

---

## 4. Le Bus de Communication Asynchrone (`agent_messages.md`)

Le bus est un fichier Markdown placé à la racine du projet. Il permet une coordination asynchrone sans réunionite ni perte d'information :

### Format d'un message standard :
```markdown
### [BE-042] Implémentation du module de notes et moyennes pondérées

| Champ | Valeur |
|---|---|
| De | Ousmane Marra — Backend Developer (Agent 03) |
| À | Abdoulaye (Frontend) ; Aïssatou Ba (QA) ; Kasongo (Agent 00) |
| Date | 2026-11-10 10:15 |
| Status | PENDING |

#### Description
Implémentation des endpoints `GET /api/grades` et `POST /api/grades`.
Respect strict de la règle BR-03 (arrondi arithmétique à 2 décimales).

#### Actions requises
- **Frontend** : Intégrer le composant avec React Query (Ticket FE-042).
- **QA** : Valider avec la suite `test_grades_module.sh`.
```

Dès que le destinataire termine l'intégration, il bascule le statut à `Status: DONE ✅`.

---

## 5. Le Moteur de Contrôle Automatisé (Kasongo & Quality Gates)

Le superviseur s'appuie sur trois scripts Python déterministes :

### 1. `audit/check_handover.py`
Contrôle avant chaque validation :
- **Périmètre Git** : compare la branche courante avec `main` et vérifie si l'agent n'a modifié que ses fichiers autorisés (ex: un frontend ne doit pas toucher à `backend/`).
- **Détection de secrets** : analyse les lignes ajoutées via Regex pour interdire les mots de passe, clés d'API, tokens JWT ou clés privées en clair.
- **Vérification du ticket** : vérifie que l'intervention possède un ticket avec statut `DONE` dans `agent_messages.md`.

### 2. `audit/check_agent_rules.py`
Contrôle les règles d'or et les cliquets anti-dette :
- **Règle R3** : Zéro en-tête `X-Tenant-Id` côté navigateur.
- **Règle R4** : Présence obligatoire de Zod et React Hook Form.
- **Règle R5 (Cliquet)** : Le nombre de fichiers appelant l'API sans React Query ne doit jamais augmenter.
- **Règle R6 (Cliquet)** : Le nombre d'occurrences de types `any` ne doit jamais dépasser la référence `agent_rules_baseline.json`.

### 3. `audit/kasongo_report.py`
Compile l'ensemble des résultats et génère un rapport officiel dans `docs/supervision/SUP-<ticket>.md` avec un verdict tranché :
- `🟢 CONFORME` : feu vert pour examen par le Tech Lead.
- `🟡 INCOMPLET` : livrables manquants.
- `🟠 À REPRENDRE` : tests ou typage en échec.
- `🔴 ESCALADE` : violation de sécurité ou modification hors périmètre.

---

## 6. L'Orchestrateur Unifié (`orchestrator.sh`)

Le script `orchestrator.sh` offre une interface en ligne de commande unifiée :

```bash
# Vérifier la santé et les règles de tous les agents
./orchestrator.sh check-agents

# Contrôler la livraison d'un agent spécifique
./orchestrator.sh handover 04 --ticket FE-QUAL-04

# Générer le rapport complet de supervision Kasongo
./orchestrator.sh kasongo 04 --ticket FE-QUAL-04

# Compiler et vérifier le build du frontend (tsc + vite)
./orchestrator.sh build

# Exécuter les 16 suites de tests d'intégration certifiées
./orchestrator.sh test

# Archiver et assainir le bus de messages
./orchestrator.sh archive-bus
```

---

## 7. Guide d'Exportation : Comment packager et réutiliser le Framework sur un autre projet

Vous pouvez transformer ce système en **un starter-kit portable (GitHub Template / Gist)** réutilisable pour n'importe quel futur projet en suivant ces 4 étapes simples :

### Étape 1 : Créer le dossier du Starter Kit
```bash
mkdir -p kasongo-framework-starter/{agents,audit,orchestration,docs/supervision}
```

### Étape 2 : Copier les briques maîtresses du framework
```bash
# 1. Copier les 12 fiches d'agents
cp agents/*.md kasongo-framework-starter/agents/

# 2. Copier les scripts d'audit et de conformité
cp audit/check_handover.py audit/check_agent_rules.py audit/kasongo_report.py kasongo-framework-starter/audit/
cp audit/agent_rules_baseline.json kasongo-framework-starter/audit/

# 3. Copier le CLI orchestrateur
cp orchestrator.sh kasongo-framework-starter/

# 4. Initialiser un bus vierge
cat << 'EOF' > kasongo-framework-starter/agent_messages.md
# 📬 Agent Message Bus — Communication Inter-Agents
> Fichier central de coordination. Consigner chaque ticket avec son statut (PENDING / DONE).
---
EOF
```

### Étape 3 : Adapter la matrice des périmètres pour votre nouvelle application
Dans `audit/check_handover.py`, adaptez la table `PERIMETRES` aux dossiers de votre nouvelle application (ex: si vous développez en Python FastAPI + Vue.js, remplacez `backend/` et `frontend/` par vos chemins réels).

### Étape 4 : Publier en tant que Template GitHub
1. Pousser le dossier dans un dépôt Git public ou privé : `github.com/<votre-nom>/agentic-coding-framework`.
2. Dans les paramètres GitHub du dépôt, cochez : **« Template repository »**.
3. Pour chaque nouveau projet, il vous suffira de cliquer sur **« Use this template »** pour démarrer immédiatement avec 12 agents spécialisés, l'orchestrateur et Kasongo préconfigurés !

---

## 8. Conclusion & Bénéfice Académique / Professionnel

Le développement de ce framework démontre une compétence de très haut niveau :
- Vous ne vous contentez pas de coder une application ; **vous concevez le système qui gouverne la production du code**.
- Pour votre mémoire et votre soutenance, ce framework constitue une **contribution méthodologique majeure** qui impressionne les jurys universitaires et les directeurs techniques d'entreprise.
- Vous disposez désormais d'un **actif technologique réutilisable à vie**, capable d'accélérer et de fiabiliser n'importe lequel de vos futurs projets logiciels.
