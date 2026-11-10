#!/usr/bin/env bash
# ==============================================================================
# 🚀 ORCHESTRATEUR AGENTIC CODING — Pipeline Multi-Agents Professionnel
# ==============================================================================
# Cet outil supervise l'avancement des agents IA, vérifie les contrats de travail,
# contrôle la présence des livrables et garantit la validation humaine.
# ==============================================================================

set -e

# Support UTF-8 pour les chemins avec accents
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Sélection automatique de la version Node.js moderne (requis pour Vite 7)
for node_dir in "$HOME/.nvm/versions/node/v22"* "$HOME/.nvm/versions/node/v20"*; do
    if [ -d "$node_dir/bin" ]; then
        export PATH="$node_dir/bin:$PATH"
        break
    fi
done

# Couleurs & Formatage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$ROOT_DIR/docs"
AGENTS_DIR="$ROOT_DIR/agents"

# Fonction d'affichage du logo
banner() {
    echo -e "${CYAN}${BOLD}"
    echo "======================================================================"
    echo "       🤖 PIPELINE AGENTIC CODING — ÉCOLE 221 / MULTI-AGENT ERP      "
    echo "======================================================================"
    echo -e "${NC}"
}

# Fonction pour vérifier l'état sémantique d'un livrable (anti-faux positifs)
check_file() {
    local file="$1"
    local name="$2"
    if [ -f "$file" ]; then
        local lines=$(wc -l < "$file")
        if [ "$lines" -lt 15 ]; then
            echo -e "  [${YELLOW}INCOMPLET${NC}]            $name (Seulement ${lines} lignes) -> $file"
            return 1
        fi

        # Détection sémantique des templates non remplis
        if grep -q -E "(\[Nom de la fonctionnalité\]|\[Titre\]|\[rôle utilisateur\]|RES-TEST-001|YYYY-MM-DD|<À ÉTABLIR>)" "$file" 2>/dev/null; then
            echo -e "  [${YELLOW}TEMPLATE NON REMPLI${NC}]  $name (Placeholders détectés) -> $file"
            return 1
        fi

        echo -e "  [${GREEN}PRÊT / CONFORME${NC}]      $name (${lines} lignes) -> $file"
        return 0
    else
        echo -e "  [${RED}MANQUANT${NC}]             $name -> $file"
        return 2
    fi
}

# Affiche le statut global du pipeline
show_status() {
    banner
    echo -e "${BOLD}📊 Tableau de Bord du Pipeline des Agents :${NC}\n"

    echo -e "${BLUE}${BOLD}--- Étape 1 : Spécifications Fonctionnelles ---${NC}"
    check_file "$DOCS_DIR/requirements.md" "Agent 01 - Product Analyst (requirements.md)" || true
    echo ""

    echo -e "${BLUE}${BOLD}--- Étape 2 : Architecture & Contrats Formels ---${NC}"
    check_file "$DOCS_DIR/architecture.md" "Agent 02 - Software Architect (architecture.md)" || true
    check_file "$DOCS_DIR/database.md"     "Agent 02 - Database Architect (database.md)" || true
    check_file "$DOCS_DIR/api-contract.md" "Agent 02 - API Contract (api-contract.md)" || true
    echo ""

    echo -e "${BLUE}${BOLD}--- Étape 3 : Backend Developer ---${NC}"
    if [ -d "$ROOT_DIR/backend" ]; then
        echo -e "  [${GREEN}MODULE PRÊT${NC}]          Dossier backend/ (Spring Boot)"
    else
        echo -e "  [${RED}ERREUR${NC}]               Dossier backend/ manquant"
    fi
    echo ""

    echo -e "${BLUE}${BOLD}--- Étape 4 : Frontend Developer ---${NC}"
    if [ -d "$ROOT_DIR/frontend" ]; then
        echo -e "  [${GREEN}MODULE PRÊT${NC}]          Dossier frontend/ (React / Vite)"
    else
        echo -e "  [${RED}ERREUR${NC}]               Dossier frontend/ manquant"
    fi
    echo ""

    echo -e "${BLUE}${BOLD}--- Étape 5 : Assurance Qualité (QA) ---${NC}"
    check_file "$DOCS_DIR/test-report.md" "Agent 05 - QA Engineer (test-report.md)" || true
    echo ""

    echo -e "${BLUE}${BOLD}--- Étape 6 : Revue de Code & Sécurité ---${NC}"
    check_file "$DOCS_DIR/review-report.md" "Agent 06 - Code Reviewer (review-report.md)" || true
    echo ""

    echo -e "${BLUE}${BOLD}--- Étape 7 : DevSecOps & Infrastructure ---${NC}"
    check_file "$DOCS_DIR/devsecops-pipeline.md" "Agent 07 - DevSecOps Engineer (devsecops-pipeline.md)" || true
    echo ""

    echo -e "${PURPLE}${BOLD}--- Bus de Messages Inter-Agents (Backend ↔ Frontend ↔ DevSecOps) ---${NC}"
    if [ -f "$ROOT_DIR/agent_messages.md" ]; then
        local pending_count=$(grep -i -E "^(- \*\*Stat(us|ut)\*\*:\s*PENDING|\|\s*Stat(us|ut)\s*\|\s*PENDING)" "$ROOT_DIR/agent_messages.md" 2>/dev/null | wc -l || true)
        local in_progress_count=$(grep -i -E "^(- \*\*Stat(us|ut)\*\*:\s*IN_PROGRESS|\|\s*Stat(us|ut)\s*\|\s*IN_PROGRESS)" "$ROOT_DIR/agent_messages.md" 2>/dev/null | wc -l || true)
        local done_count=$(grep -i -E "^(- \*\*Stat(us|ut)\*\*:\s*DONE|\|\s*Stat(us|ut)\s*\|\s*DONE)" "$ROOT_DIR/agent_messages.md" 2>/dev/null | wc -l || true)
        echo -e "  📬 agent_messages.md : ${YELLOW}$pending_count PENDING${NC} | ${CYAN}$in_progress_count IN_PROGRESS${NC} | ${GREEN}$done_count DONE${NC}"
    else
        echo -e "  [${RED}MANQUANT${NC}] agent_messages.md"
    fi
    echo ""
}

# Audit automatique de sécurité rapide et approfondi
audit_code() {
    banner
    echo -e "${BOLD}🔍 Audit de Sécurité, Contrats & Multi-Tenancy :${NC}\n"

    echo -e "1. Vérification de l'isolation Multi-Tenancy (@TenantId)..."
    if python3 "$ROOT_DIR/check_multi_tenancy.py"; then
        echo -e "${GREEN}✅ Annotations multi-tenant présentes sur les entités (ne prouve PAS l étanchéité : voir test_tenant_isolation_module.sh).${NC}\n"
    else
        echo -e "${RED}❌ Échec de l'audit multi-tenancy. Corrigez les entités signalées.${NC}\n"
    fi

    echo -e "2. Vérification Contract-First & Anti-Dérive (docs/api-contract.md)..."
    if python3 "$ROOT_DIR/validate_contracts.py"; then
        echo -e "${GREEN}✅ Contrats API synchronisés et validés.${NC}\n"
    else
        echo -e "${RED}❌ Dérive contractuelle détectée. Harmonisez le contrat et le code.${NC}\n"
    fi

    echo -e "3. Recherche de secrets potentiels (API keys, mots de passe hardcodés)..."
    local secrets_found=0
    if grep -r -E "(password\s*=\s*['\"][^'\"]{6,}['\"]|secret\s*=\s*['\"][^'\"]{6,}['\"])" "$ROOT_DIR/backend/src" "$ROOT_DIR/frontend/src" 2>/dev/null; then
        echo -e "${RED}⚠️  ATTENTION : Mots de passe ou secrets détectés en clair !${NC}\n"
        secrets_found=1
    else
        echo -e "${GREEN}✅ Aucun mot de passe hardcodé détecté.${NC}\n"
    fi

    echo -e "4. Recherche de console.log résiduels dans le frontend..."
    local logs_found=$(grep -r "console.log" "$ROOT_DIR/frontend/src" 2>/dev/null | wc -l || true)
    if [ "$logs_found" -gt 0 ]; then
        echo -e "${YELLOW}ℹ️  $logs_found console.log trouvés dans le code frontend.${NC}\n"
    else
        echo -e "${GREEN}✅ Code frontend propre (zéro console.log résiduel).${NC}\n"
    fi

    echo -e "5. Vérification de la présence des livrables obligatoires..."
    if [ -f "$DOCS_DIR/requirements.md" ] && [ -f "$DOCS_DIR/api-contract.md" ] && [ -f "$DOCS_DIR/test-report.md" ]; then
        echo -e "${GREEN}✅ Tous les livrables indispensables sont présents.${NC}"
    else
        echo -e "${RED}❌ Livrables incomplets. Complétez les étapes précédentes avant de merger.${NC}"
    fi
}

# Exécution des tests d'intégration avec certification des logs & pre-flight check
run_tests() {
    banner
    echo -e "${BOLD}🧪 Lancement de la Suite de Tests QA Certifiée :${NC}\n"

    echo -e "Vérification de la disponibilité du backend sur http://localhost:${QA_PORT:-8090}/api..."
    if ! curl -s -m 2 http://localhost:${QA_PORT:-8090}/api/auth/me >/dev/null 2>&1 && ! curl -s -m 2 http://localhost:${QA_PORT:-8090}/ >/dev/null 2>&1; then
        echo -e "${RED}❌ Le serveur backend Spring Boot n'est pas détecté sur le port ${QA_PORT:-8090}.${NC}"
        echo -e "${YELLOW}   Pour lancer le backend en local :${NC}"
        echo -e "   cd \"$ROOT_DIR/backend\" && ./mvnw spring-boot:run"
        echo -e "${YELLOW}   Ou avec Docker :${NC}"
        echo -e "   docker-compose up -d\n"
        return 1
    fi
    echo -e "${GREEN}✅ Backend opérationnel et réactif sur le port ${QA_PORT:-8090}.${NC}\n"

    # Identifiants de test lus depuis backend/.env (jamais en dur dans les scripts)
    if [ -z "${SUPER_ADMIN_PASSWORD:-}" ] && [ -f "$ROOT_DIR/backend/.env" ]; then
        SUPER_ADMIN_PASSWORD=$(grep -E '^SUPER_ADMIN_PASSWORD=' "$ROOT_DIR/backend/.env" | tail -n 1 | cut -d= -f2-)
        export SUPER_ADMIN_PASSWORD
    fi
    if [ -z "${SUPER_ADMIN_PASSWORD:-}" ]; then
        echo -e "${RED}❌ SUPER_ADMIN_PASSWORD absent (export ou backend/.env).${NC}"
        return 1
    fi

    # Base du backend de QA visé (écrite par qa/start_backend.sh) : prime sur backend/.env
    if [ -f "$ROOT_DIR/qa/.qa_env_${QA_PORT:-8090}" ]; then
        set -a; . "$ROOT_DIR/qa/.qa_env_${QA_PORT:-8090}"; set +a
    fi

    # Données de départ QA (idempotent) : la suite ne dépend plus d'une base remplie à la main
    if ! bash "$ROOT_DIR/qa/load_fixtures.sh"; then
        echo -e "${RED}❌ Données QA non chargées : tests non lancés.${NC}"
        return 1
    fi
    echo ""

    mkdir -p "$ROOT_DIR/logs"
    local log_file="$ROOT_DIR/logs/qa_execution.log"
    echo "--- Exécution des tests QA certifiée : $(date '+%Y-%m-%d %H:%M:%S') ---" > "$log_file"

    if [ -f "$ROOT_DIR/run_all_integration_tests.sh" ]; then
        echo -e "${CYAN}Exécution de ./run_all_integration_tests.sh (sortie capturée dans logs/qa_execution.log)...${NC}"
        # PIPESTATUS[0] = code de sortie des tests (et non celui de tee)
        # Les jetons JWT (corps, cookies) sont masqués avant d'atteindre l'écran et le journal
        bash "$ROOT_DIR/run_all_integration_tests.sh" 2>&1 \
            | sed -u -E 's/eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+/<jwt masqué>/g' | tee -a "$log_file"
        local test_status=${PIPESTATUS[0]}
        if [ "$test_status" -eq 0 ]; then
            echo "QA_RESULT: PASS" >> "$log_file"
            echo -e "\n${GREEN}✅ Tests validés avec succès. Log de preuve certifié : $log_file${NC}"
        else
            echo "QA_RESULT: FAIL (exit $test_status)" >> "$log_file"
            echo -e "\n${RED}❌ Des tests ont échoué (exit $test_status). Log d'anomalies : $log_file${NC}"
            return 1
        fi
    else
        echo -e "${RED}Script run_all_integration_tests.sh introuvable.${NC}"
        return 1
    fi
}

# Gestion de l'isolation Git (Feature Branch & Rollback)
branch_feature() {
    local feature_name="$1"
    if [ -z "$feature_name" ]; then
        echo -e "${RED}Usage : ./orchestrator.sh branch <nom-de-la-feature>${NC}"
        return 1
    fi
    banner
    echo -e "${BOLD}🌿 Création d'une branche isolée pour la fonctionnalité : ${CYAN}feature/$feature_name${NC}\n"
    git checkout -b "feature/$feature_name"
    echo -e "${GREEN}✅ Branche feature/$feature_name créée et active. Vous pouvez travailler en toute sécurité.${NC}"
}

# Moteur de Passage de Témoin Automatique (Handover)
detect_next_step() {
    banner
    echo -e "${BOLD}🎯 Moteur d'Orchestration Continue — Prochaine Action :${NC}\n"

    # 1. Vérification des tickets en attente sur le bus
    if [ -f "$ROOT_DIR/agent_messages.md" ]; then
        local pending_be=$(awk '/^## 📤 Messages du Backend/{flag=1; next} /^## 📥 Messages/{flag=0} flag && /Stat(us|ut).*PENDING/{print $0}' "$ROOT_DIR/agent_messages.md" 2>/dev/null || true)
        local pending_fe=$(awk '/^## 📥 Messages du Frontend/{flag=1; next} /^## 🛡️ Messages/{flag=0} flag && /Stat(us|ut).*PENDING/{print $0}' "$ROOT_DIR/agent_messages.md" 2>/dev/null || true)

        if [ -n "$pending_be" ]; then
            echo -e "🔔 ${YELLOW}TICKET EN ATTENTE CÔTÉ FRONTEND${NC}"
            echo -e "👉 ${BOLD}Agent Actif : Agent 04 — Frontend Developer${NC}"
            echo -e "   Mission : Consommer les nouveaux endpoints livrés par le Backend."
            echo -e "   Fiche : agents/04_frontend_developer.md"
            echo -e "   Action : Intégrer l'API dans frontend/src/ puis basculer le ticket à 'status: DONE ✅'."
            return 0
        fi

        if [ -n "$pending_fe" ]; then
            echo -e "🔔 ${YELLOW}RETOUR D'INTÉGRATION BLOQUANT CÔTÉ BACKEND${NC}"
            echo -e "👉 ${BOLD}Agent Actif : Agent 03 — Backend Developer${NC}"
            echo -e "   Mission : Corriger le contrôleur/service selon le besoin exprimé par le Frontend."
            echo -e "   Fiche : agents/03_backend_developer.md"
            echo -e "   Action : Ajuster le code Java puis basculer le ticket à 'status: DONE ✅'."
            return 0
        fi
    fi

    # 2. Vérification des livrables du cycle
    if [ ! -f "$DOCS_DIR/requirements.md" ]; then
        echo -e "👉 ${BOLD}Agent Actif : Agent 01 — Product Analyst${NC}"
        echo -e "   Mission : Rédiger docs/requirements.md (User Stories Gherkin et règles métier)."
        return 0
    fi

    # 3. Vérification du rapport de tests
    local log_file="$ROOT_DIR/logs/qa_execution.log"
    if [ ! -f "$log_file" ] || [ $(find "$log_file" -mmin +120 2>/dev/null | wc -l) -gt 0 ]; then
        echo -e "👉 ${BOLD}Agent Actif : Agent 05 — QA Engineer${NC}"
        echo -e "   Mission : Exécuter la suite de tests certifiée et actualiser docs/test-report.md."
        echo -e "   Commande : ./orchestrator.sh test"
        return 0
    fi

    # 4. Le log récent doit contenir un verdict PASS explicite
    if ! grep -q "^QA_RESULT: PASS" "$log_file"; then
        echo -e "🔴 ${RED}DERNIÈRE EXÉCUTION QA EN ÉCHEC OU SANS VERDICT${NC} ($log_file)"
        echo -e "👉 ${BOLD}Agent Actif : Agent 03/04 — corriger, puis relancer ./orchestrator.sh test${NC}"
        return 0
    fi

    # 5. Aucune dérive contractuelle tolérée
    if ! python3 "$ROOT_DIR/validate_contracts.py" >/dev/null 2>&1; then
        echo -e "🔴 ${RED}DÉRIVE CONTRACTUELLE DÉTECTÉE${NC}"
        echo -e "👉 ${BOLD}Agent Actif : Agent 02 — Software Architect${NC}"
        echo -e "   Détail : ./orchestrator.sh check-contract"
        return 0
    fi

    # 6. Revue de code (Agent 06) puis 7. DevSecOps (Agent 07) : verdict positif + preuves fraîches citées
    if ! report_ok "$DOCS_DIR/review-report.md" '^\**VERDICT: APPROVED(_WITH_COMMENTS)?\b'; then
        echo -e "🔍 ${YELLOW}REVUE DE CODE NON APPROUVÉE, OU SANS FICHIER DE PREUVES À JOUR${NC}"
        echo -e "👉 ${BOLD}Agent Actif : Agent 06 — Code Reviewer${NC} (agents/06_code_reviewer.md)"
        echo -e "   Préalable : ./orchestrator.sh evidence  → citer le fichier produit dans docs/review-report.md"
        return 0
    fi
    if ! report_ok "$DOCS_DIR/devsecops-pipeline.md" '^\**VERDICT DEVSECOPS: GO\b'; then
        echo -e "🛡️ ${YELLOW}DEVSECOPS : PAS DE GO, OU SANS FICHIER DE PREUVES À JOUR${NC}"
        echo -e "👉 ${BOLD}Agent Actif : Agent 07 — DevSecOps Engineer${NC} (agents/07_devsecops_engineer.md)"
        echo -e "   Préalable : ./orchestrator.sh evidence  → citer le fichier produit dans docs/devsecops-pipeline.md"
        return 0
    fi

    local qa_date=$(head -n 1 "$log_file" | sed 's/^--- //; s/ ---$//')
    echo -e "${GREEN}🎉 PIPELINE VERT : QA PASS, contrat conforme, revue APPROVED, DevSecOps GO.${NC}"
    echo -e "   - Dernière $qa_date"

    # 8. Vérification gate Kasongo : rapport SUP récent ?
    local last_sup
    last_sup=$(ls -t "$ROOT_DIR/docs/supervision/SUP-"*.md 2>/dev/null | head -1)
    if [ -z "$last_sup" ]; then
        echo -e ""
        echo -e "🕵️  ${YELLOW}GATE KASONGO REQUIS${NC}"
        echo -e "   Aucun rapport de supervision trouvé dans docs/supervision/."
        echo -e "   👉 Lancez : ${CYAN}./orchestrator.sh kasongo <NN> [--ticket ID]${NC}"
        return 0
    fi
    # Dernière modification du rapport vs dernier commit de code
    local sup_time code_time
    sup_time=$(stat -c %Y "$last_sup" 2>/dev/null || echo 0)
    code_time=$(for d in backend frontend; do git -C "$ROOT_DIR/$d" log -1 --format=%ct 2>/dev/null; done | sort -n | tail -1)
    if [ "${sup_time:-0}" -lt "${code_time:-0}" ]; then
        echo -e ""
        echo -e "🕵️  ${YELLOW}GATE KASONGO REQUIS${NC}"
        echo -e "   Le dernier rapport Kasongo ($(basename "$last_sup")) est antérieur au dernier commit de code."
        echo -e "   👉 Relancez : ${CYAN}./orchestrator.sh kasongo <NN> [--ticket ID]${NC}"
        return 0
    fi

    echo -e "   - 🕵️  Kasongo : $(basename "$last_sup") ✅"
    echo -e "   - 👤 ${BOLD}En attente de la validation du Tech Lead humain${NC} (seul décideur du merge et du déploiement)."
}

# Rapport valide = verdict attendu + fichier de preuves cité, existant et postérieur au dernier commit de code
report_ok() {
    local report="$1" verdict_regex="$2" ev ev_time code_time
    [ -f "$report" ] && grep -qE "$verdict_regex" "$report" || return 1
    ev=$(grep -oE 'docs/evidence/evidence-[0-9]{8}-[0-9]{6}\.md' "$report" | tail -n 1)
    [ -n "$ev" ] && [ -f "$ROOT_DIR/$ev" ] || return 1
    ev_time=$(date -d "$(echo "$ev" | sed -E 's/.*evidence-([0-9]{4})([0-9]{2})([0-9]{2})-([0-9]{2})([0-9]{2})([0-9]{2}).*/\1-\2-\3 \4:\5:\6/')" +%s)
    code_time=$(for d in backend frontend; do git -C "$ROOT_DIR/$d" log -1 --format=%ct 2>/dev/null; done | sort -n | tail -1)
    [ "$ev_time" -ge "${code_time:-0}" ]
}

rollback_changes() {
    banner
    echo -e "${BOLD}⏪ Rollback de Sécurité : Annulation des modifications non commitées${NC}\n"
    git restore .
    git clean -fd -e node_modules -e target
    echo -e "${GREEN}✅ Espace de travail réinitialisé au dernier commit propre.${NC}"
}

# Aide / Menu
show_help() {
    banner
    echo -e "${BOLD}Commandes disponibles :${NC}"
    echo -e "  ${CYAN}./orchestrator.sh status${NC}           -> Affiche l'état d'avancement des agents et des livrables"
    echo -e "  ${CYAN}./orchestrator.sh audit${NC}            -> Audit de sécurité, multi-tenancy et propreté du code"
    echo -e "  ${CYAN}./orchestrator.sh test${NC}             -> Exécute la suite de tests avec pre-flight check et logs"
    echo -e "  ${CYAN}./orchestrator.sh up [services]${NC}   -> Démarre l'environnement (docker compose, défaut : backend) et attend l'API"
    echo -e "  ${CYAN}./orchestrator.sh run <NN> \"tâche\"${NC} -> Exécute un agent via l'API Claude (--budget, --max-turns, --dry-run)"
    echo -e "  ${CYAN}./orchestrator.sh convoquer <NN> <TICKET>${NC} -> Kasongo convoque un agent « À REPRENDRE » (--simulation)"
    echo -e "  ${CYAN}./orchestrator.sh kasongo <NN>${NC}     -> Kasongo (00) : rapport complet de supervision + DoD (--ticket, --base, --out)"
    echo -e "  ${CYAN}./orchestrator.sh handover <NN>${NC}    -> Kasongo (00) : contrôle la livraison d'un agent (--ticket, --base, --only)"
    echo -e "  ${CYAN}./orchestrator.sh diagrams${NC}         -> Diagrammes BD / classes générés depuis le code (--check, --render)"
    echo -e "  ${CYAN}./orchestrator.sh guardian${NC}         -> Memoire Guardian AI : audit académique, détection IA, soutenance et livrables"
    echo -e "  ${CYAN}./orchestrator.sh check-agents${NC}     -> Vérifie que le code respecte les règles vérifiables des fiches"
    echo -e "  ${CYAN}./orchestrator.sh backfill-memberships${NC} -> SEC-003 : reprise des appartenances (simulation ; --apply pour écrire)"
    echo -e "  ${CYAN}./orchestrator.sh evidence${NC}         -> Preuves machine datées pour les agents 06/07 (docs/evidence/)"
    echo -e "  ${CYAN}./orchestrator.sh fixtures${NC}         -> Charge les comptes et écoles de test (qa/fixtures.sql)"
    echo -e "  ${CYAN}./orchestrator.sh build${NC}            -> Vérifie la compilation TypeScript / Vite"
    echo -e "  ${CYAN}./orchestrator.sh devsecops${NC}        -> Audit complet DevSecOps (Docker, secrets, env)"
    echo -e "  ${CYAN}./orchestrator.sh archive-bus${NC}      -> Archive les messages terminés (--dry-run, --repair-archive)"
    echo -e "  ${CYAN}./orchestrator.sh audit-tenancy${NC}    -> Scanne les entités JPA pour garantir l'isolation @TenantId"
    echo -e "  ${CYAN}./orchestrator.sh check-contract${NC}   -> Vérifie la conformité formelle de docs/api-contract.md"
    echo -e "  ${CYAN}./orchestrator.sh next${NC}             -> Analyse l'état et désigne le prochain agent à agir
  ${CYAN}./orchestrator.sh branch <nom>${NC}     -> Crée une branche Git isolée pour un agent"
    echo -e "  ${CYAN}./orchestrator.sh rollback${NC}         -> Annule en toute sécurité les modifications d'un agent"
    echo -e "  ${CYAN}./orchestrator.sh agents${NC}           -> Liste les fiches de poste des agents (00 : Kasongo superviseur, 01-07 : chaîne de livraison, 08 à 11 : Business, Rédaction, Release, Modélisation)"
    echo ""
}

# Audit DevSecOps
run_devsecops() {
    banner
    echo -e "${BOLD}🛡️ Audit DevSecOps & Sécurité de l'Infrastructure :${NC}\n"

    echo -e "1. Vérification des Dockerfiles & Conteneurs..."
    if [ -f "$ROOT_DIR/backend/Dockerfile" ]; then
        echo -e "  ${GREEN}✅ Backend Dockerfile trouvé.${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Backend Dockerfile manquant.${NC}"
    fi
    if [ -f "$ROOT_DIR/frontend/Dockerfile" ]; then
        echo -e "  ${GREEN}✅ Frontend Dockerfile trouvé.${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Frontend Dockerfile manquant.${NC}"
    fi

    echo -e "\n2. Vérification des variables d'environnement & .gitignore..."
    if grep -q "^\.env" "$ROOT_DIR/.gitignore" 2>/dev/null || grep -q "^\.env" "$ROOT_DIR/backend/.gitignore" 2>/dev/null; then
        echo -e "  ${GREEN}✅ .env est correctement ignoré par Git.${NC}"
    else
        echo -e "  ${RED}❌ DANGER : .env n'est pas explicitement dans .gitignore !${NC}"
    fi

    echo -e "\n3. Scan de présence de secrets dans le code..."
    local sec_count=0
    if grep -r -i -E "(api_key\s*=\s*['\"][0-9a-zA-Z_-]{16,}['\"]|jwt_secret\s*=\s*['\"][^'\"]{10,}['\"])" "$ROOT_DIR/backend/src" "$ROOT_DIR/frontend/src" 2>/dev/null; then
        echo -e "  ${RED}❌ Secret hardcodé détecté !${NC}"
        sec_count=$((sec_count + 1))
    else
        echo -e "  ${GREEN}✅ Aucun secret critique en dur trouvé dans les sources.${NC}"
    fi

    echo -e "\n4. État du livrable DevSecOps..."
    check_file "$DOCS_DIR/devsecops-pipeline.md" "docs/devsecops-pipeline.md"
}

# Build du frontend
build_project() {
    banner
    echo -e "${BOLD}📦 Compilation et Build Frontend :${NC}\n"
    (cd "$ROOT_DIR/frontend" && npm run build)
}

# Liste des agents
list_agents() {
    banner
    echo -e "${BOLD}👥 Équipe d'Agents Spécialisés :${NC}\n"
    for agent in "$AGENTS_DIR"/*.md; do
        if [ -f "$agent" ]; then
            echo -e "  📄 ${BOLD}$(basename "$agent")${NC}"
            head -n 5 "$agent" | sed 's/^/     /'
            echo ""
        fi
    done
}

# Démarre l'environnement cible (docker compose) et attend que l'API réponde
start_env() {
    local services=("$@")
    [ ${#services[@]} -gt 0 ] || services=(backend)
    echo -e "${BOLD}🚀 docker compose up -d ${services[*]}${NC}"
    docker compose -f "$ROOT_DIR/docker-compose.yml" up -d "${services[@]}" || exit 1
    for _ in $(seq 1 60); do
        code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 http://localhost:${QA_PORT:-8090}/api/ || true)"
        if [ -n "$code" ] && [ "$code" != "000" ]; then
            echo -e "${GREEN}✅ API joignable sur localhost:${QA_PORT:-8090} (HTTP $code).${NC}"
            return 0
        fi
        sleep 2
    done
    echo -e "${RED}❌ ENV_OFFLINE : l'API ne répond pas après 120 s (docker compose logs backend).${NC}"
    exit 1
}

# Routage des commandes
case "$1" in
    status)
        show_status
        ;;
    audit)
        audit_code
        ;;
    test)
        run_tests
        ;;
    build)
        build_project
        ;;
    devsecops)
        run_devsecops
        ;;
    up)
        shift
        start_env "$@"
        ;;
    run)
        # Exécute un agent sur l'API Claude (clé dans .env.agents) : run <NN> "<tâche>" [--budget] [--dry-run]
        shift
        python3 "$ROOT_DIR/orchestration/agent_runtime.py" "$@"
        ;;
    convoquer)
        # Kasongo convoque un agent jugé « À REPRENDRE » : convocations, remplaçant, puis escalade
        shift
        python3 "$ROOT_DIR/orchestration/convocation.py" "$@"
        ;;
    kasongo)
        # Kasongo (Agent 00) : rapport complet de supervision (handover + DoD + rapport Markdown)
        shift
        python3 "$ROOT_DIR/audit/kasongo_report.py" "$@"
        ;;
    handover)
        # Kasongo (Agent 00) : contrôle automatique d'une livraison d'agent (périmètre, secrets, ticket)
        shift
        python3 "$ROOT_DIR/audit/check_handover.py" "$@"
        ;;
    diagrams)
        # Diagrammes « tel que construit » (Agent 11) : --check (écart avec le code), --render (PNG)
        shift
        python3 "$ROOT_DIR/audit/gen_diagrams.py" "$@"
        ;;
    guardian)
        # Memoire Guardian AI (Agent 12) : audit académique en 7 phases, score /100, soutenance, checklist
        shift
        python3 "$ROOT_DIR/audit/memoire_guardian.py" "$@"
        ;;
    check-agents)
        python3 "$ROOT_DIR/audit/check_agent_rules.py"
        ;;
    backfill-memberships)
        shift
        bash "$ROOT_DIR/ops/backfill_memberships.sh" "$@"
        ;;
    evidence)
        bash "$ROOT_DIR/audit/collect_evidence.sh"
        ;;
    fixtures)
        bash "$ROOT_DIR/qa/load_fixtures.sh"
        ;;
    archive-bus)
        # Tests de non-régression du bus AVANT toute écriture (options : --dry-run, --keep N, --repair-archive)
        if ! python3 -m unittest discover -s "$ROOT_DIR/tests" -p "test_archive_bus.py" -q; then
            echo -e "${RED}❌ Tests du bus en échec : agent_messages.md n'a pas été modifié.${NC}"
            exit 1
        fi
        shift
        python3 "$ROOT_DIR/archive_agent_messages.py" "$@"
        ;;
    audit-tenancy)
        python3 "$ROOT_DIR/check_multi_tenancy.py"
        ;;
    check-contract)
        python3 "$ROOT_DIR/validate_contracts.py"
        ;;
    agents)
        list_agents
        ;;
    next)
        detect_next_step
        ;;
    branch)
        branch_feature "$2"
        ;;
    rollback)
        rollback_changes
        ;;
    *)
        show_help
        ;;
esac

