#!/usr/bin/env bash
# ==============================================================================
# Collecte des PREUVES MACHINE exigées par l'Agent 06 (Code Reviewer) et l'Agent 07 (DevSecOps).
# Écrit la sortie BRUTE de chaque contrôle dans docs/evidence/evidence-<date>.md (versionné).
#   PASS   : contrôle exécuté et conforme
#   FAIL   : contrôle exécuté et non conforme
#   ABSENT : contrôle impossible (outil manquant…) → ce n'est PAS un succès
# Code de sortie : 0 seulement si 0 FAIL et 0 ABSENT. Les secrets trouvés sont masqués (--redact).
# ==============================================================================
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
TS="$(date '+%Y%m%d-%H%M%S')"
OUT="docs/evidence/evidence-$TS.md"
BODY="$(mktemp)"
PASS=0 FAIL=0 ABSENT=0
GITLEAKS_IMAGE="zricethezav/gitleaks:v8.18.4"

record() {  # record <titre> <PASS|FAIL|ABSENT> <commande> <sortie>
  local icon
  case "$2" in PASS) PASS=$((PASS + 1)); icon="🟢" ;; FAIL) FAIL=$((FAIL + 1)); icon="🔴" ;; *) ABSENT=$((ABSENT + 1)); icon="⚪" ;; esac
  { printf '## %s %s — %s\n\nCommande : `%s`\n\n```text\n' "$icon" "$1" "$2" "$3"
    printf '%s\n' "$4" | sed 's/\x1b\[[0-9;]*m//g' | tail -n 40
    printf '```\n\n'; } >> "$BODY"
  echo "  $icon $2  $1"
}
run() { OUTPUT="$("$@" 2>&1)"; RC=$?; }

echo "🔎 Collecte des preuves → $OUT"

# 1-2. Outils maison du pipeline
run python3 check_multi_tenancy.py
record "Isolation multi-tenant" "$([ $RC -eq 0 ] && echo PASS || echo FAIL)" "python3 check_multi_tenancy.py" "$OUTPUT"
run python3 validate_contracts.py
record "Contrat d'API (front ↔ back ↔ contrat)" "$([ $RC -eq 0 ] && echo PASS || echo FAIL)" "python3 validate_contracts.py" "$OUTPUT"

# 3. Dernière campagne QA : PASS et postérieure au dernier commit des 3 dépôts
LOG="logs/qa_execution.log"
if [ -f "$LOG" ]; then
  LAST_COMMIT=$(for d in backend frontend; do git -C "$d" log -1 --format=%ct 2>/dev/null; done | sort -n | tail -1)   # dernier commit de CODE applicatif
  LOG_TIME=$(stat -c %Y "$LOG")
  QA_LINE="$(grep -E '^QA_RESULT' "$LOG" | tail -1)"
  INFO="$(head -1 "$LOG")
$QA_LINE
Log : $(date -d "@$LOG_TIME" '+%F %T') — dernier commit de code : $(date -d "@$LAST_COMMIT" '+%F %T')"
  STATUS=FAIL; [[ "$QA_LINE" == "QA_RESULT: PASS" && $LOG_TIME -ge $LAST_COMMIT ]] && STATUS=PASS
  record "Campagne QA à jour" "$STATUS" "./orchestrator.sh test" "$INFO"
else
  record "Campagne QA à jour" ABSENT "./orchestrator.sh test" "Aucun $LOG : lancer la campagne QA."
fi

# 4. @PreAuthorize n'agit que si @EnableMethodSecurity est déclaré
PRE=$(grep -rhE "^\s*@PreAuthorize\(" backend/src/main/java | wc -l)   # annotations réelles, pas les commentaires
ENABLED=$(grep -rlE "^\s*@Enable(Global)?MethodSecurity\b" backend/src/main/java | wc -l)
STATUS=PASS; [ "$PRE" -gt 0 ] && [ "$ENABLED" -eq 0 ] && STATUS=FAIL
record "Sécurité par méthode active" "$STATUS" "grep @PreAuthorize / @EnableMethodSecurity" \
  "@PreAuthorize : $PRE occurrence(s) — @EnableMethodSecurity : $ENABLED fichier(s)
$([ "$STATUS" = FAIL ] && echo "→ les @PreAuthorize sont DÉCORATIFS : seules les règles d'URL de SecurityConfig s'appliquent.")"

# 5. Secrets dans l'historique git (gitleaks, secrets masqués)
if command -v gitleaks >/dev/null; then GL=(gitleaks)
elif docker image inspect "$GITLEAKS_IMAGE" >/dev/null 2>&1 || docker pull -q "$GITLEAKS_IMAGE" >/dev/null 2>&1; then GL=(docker run --rm -u "$(id -u):$(id -g)" -v "$ROOT:/r:ro" "$GITLEAKS_IMAGE")
else GL=(); fi
if [ ${#GL[@]} -gt 0 ]; then
  OUTPUT=""; STATUS=PASS
  for d in . backend frontend; do
    src="$ROOT/$d"; [ "${GL[0]}" = docker ] && src="/r/$d"
    R="$("${GL[@]}" detect --source="$src" --no-banner --redact -v 2>&1 | sed 's/\x1b\[[0-9;]*m//g')"
    N="$(echo "$R" | grep -oE 'leaks found: [0-9]+' | grep -oE '[0-9]+' || echo 0)"
    [ "${N:-0}" -gt 0 ] && STATUS=FAIL
    OUTPUT+="── dépôt $d : ${N:-0} fuite(s)
$(echo "$R" | grep -E '^(RuleID|File):' | paste - - | sort | uniq -c | head -12)
"
  done
  record "Secrets dans l'historique git (gitleaks)" "$STATUS" "gitleaks detect --redact (3 dépôts)" "$OUTPUT"
else
  record "Secrets dans l'historique git (gitleaks)" ABSENT "gitleaks" "Ni gitleaks ni docker disponibles."
fi

# 6. Mots de passe littéraux dans le code suivi (gitleaks ne les voit pas) — emplacements seulement
#    Les tests unitaires (src/test/) utilisent des valeurs factices assumées : exclus du contrôle.
#    firebase.ts : clé d'API web Firebase, publique par conception (protégée par les règles Firebase).
#    secret(?!aire) : le rôle SECRETAIRE n'est pas un secret.
PATTERN='(?i)(password|passwd|secret(?!aire)|api[_-]?key)\w*["'"'"']?\s*[:=]\s*["'"'"'][^"'"'"'$\s{]{6,}["'"'"']'
HITS="$(for d in . backend frontend; do git -C "$d" ls-files -z -- '*.java' '*.ts' '*.tsx' '*.sh' '*.yml' '*.yaml' '*.properties' '*.json' \
  | (cd "$d" && xargs -0 grep -nP "$PATTERN" 2>/dev/null) | grep -vE 'change_me|your_|example|placeholder' | grep -vE '^(.*/)?src/test/' | grep -v '^src/core/firebase/firebase.ts:' | cut -d: -f1,2 | sed "s#^#$d/#"; done)"
# Valeurs NON entre guillemets dans la configuration (YAML / properties) : « password: valeur » (faux négatif relevé par l'Agent 07)
PATTERN_CONF='(?i)^\s*[\w.-]*(password|passwd|secret(?!aire)|api[_-]?key)[\w.-]*\s*[:=]\s*(?![\s$"'"'"'{]|$)\S{6,}'
HITS_CONF="$(for d in . backend frontend; do git -C "$d" ls-files -z -- '*.yml' '*.yaml' '*.properties' \
  | (cd "$d" && xargs -0 grep -nP "$PATTERN_CONF" 2>/dev/null) | grep -vE '^(.*/)?src/test/|change_me|your_|example|placeholder|ci-only-' | cut -d: -f1,2 | sed "s#^#$d/#"; done)"
HITS="$(printf '%s\n%s\n' "$HITS" "$HITS_CONF" | grep . | sort -u)"
ENVS="$(for d in . backend frontend; do git -C "$d" ls-files | grep -E '(^|/)\.env$' | sed "s#^#$d/#"; done)"
STATUS=PASS; [ -n "$HITS$ENVS" ] && STATUS=FAIL
record "Mots de passe en dur / .env versionnés" "$STATUS" "grep -P (password|secret|apikey)=\"…\" sur fichiers suivis" \
  "Fichiers .env suivis : ${ENVS:-aucun}
Littéraux (fichier:ligne) : $(echo "$HITS" | grep -c . )
$(echo "$HITS" | head -25)"

# 7. Conteneurs : utilisateur non-root dans l'étape finale + exposition / secrets du compose
OUTPUT=""; STATUS=PASS
for f in backend/Dockerfile frontend/Dockerfile; do
  U="$(awk '/^FROM /{u=""} /^USER /{u=$2} END{print u}' "$f")"
  if [ -z "$U" ] || [[ "$U" =~ ^(root|0)(:|$) ]]; then STATUS=FAIL; OUTPUT+="$f : étape finale SANS USER non-root (tourne en root)
"; else OUTPUT+="$f : USER $U
"; fi
done
PUB="$(grep -nE '^\s+- "?[0-9]+:[0-9]+' docker-compose.yml)"   # sans 127.0.0.1 devant
[ -n "$PUB" ] && STATUS=FAIL
LIT="$(grep -nE '^\s*-?\s*[A-Z_]*(PASSWORD|SECRET)[A-Z_]*\s*[:=]\s*[^$ ]' docker-compose.yml | cut -d: -f1 | sed 's/^/ligne /')"
[ -n "$LIT" ] && STATUS=FAIL
OUTPUT+="Ports publiés sur toutes les interfaces (0.0.0.0) :
$PUB
Secrets littéraux dans docker-compose.yml : ${LIT:-aucun}"
record "Conteneurs & docker-compose" "$STATUS" "awk USER Dockerfile ; grep ports/PASSWORD docker-compose.yml" "$OUTPUT"

# 8. Règles des fiches d'agents ↔ code (une fiche « Conforme » ne prouve rien)
run python3 audit/check_agent_rules.py
record "Règles des fiches d'agents respectées par le code" "$([ $RC -eq 0 ] && echo PASS || echo FAIL)" "python3 audit/check_agent_rules.py" "$OUTPUT"

# 9-10. Dépendances vulnérables (SCA)
NPM="$(cd frontend && npm audit --omit=dev --json 2>/dev/null)"   # code retour ≠ 0 dès qu'il y a une vulnérabilité : on lit le JSON
if [ -n "$NPM" ] && echo "$NPM" | jq -e .metadata >/dev/null 2>&1; then
  V="$(echo "$NPM" | jq -r '.metadata.vulnerabilities | "critical=\(.critical) high=\(.high) moderate=\(.moderate) low=\(.low)"')"
  HC="$(echo "$NPM" | jq '.metadata.vulnerabilities.critical + .metadata.vulnerabilities.high')"
  record "Dépendances npm (frontend, prod)" "$([ "$HC" -eq 0 ] && echo PASS || echo FAIL)" "npm audit --omit=dev" "$V"
else
  record "Dépendances npm (frontend, prod)" ABSENT "npm audit --omit=dev" "npm audit indisponible (réseau / registre)."
fi
# Maven : SBOM CycloneDX (compile/runtime) puis osv-scanner dans Docker (APP-SEC-09)
SBOM_DIR="$(mktemp -d)"
if (cd backend && mvn -q -B -ntp org.cyclonedx:cyclonedx-maven-plugin:2.9.1:makeBom \
      -DoutputFormat=json -DoutputDirectory="$SBOM_DIR" -DincludeTestScope=false) >/dev/null 2>&1 \
   && [ -s "$SBOM_DIR/bom.json" ] && command -v docker >/dev/null; then
  OSV="$(docker run --rm -v "$SBOM_DIR:/sbom:ro" ghcr.io/google/osv-scanner:v1.9.1 --format json --sbom=/sbom/bom.json 2>/dev/null)"
  if echo "$OSV" | jq -e .results >/dev/null 2>&1; then
    NB="$(echo "$OSV" | jq '[.results[].packages[]] | length')"
    LISTE="$(echo "$OSV" | jq -r '[.results[].packages[].package | "\(.name):\(.version)"] | join(", ")')"
    record "Dépendances Maven (backend)" "$([ "$NB" -eq 0 ] && echo PASS || echo FAIL)" "SBOM CycloneDX + osv-scanner v1.9.1" \
      "$([ "$NB" -eq 0 ] && echo "Aucune vulnérabilité connue." || echo "$NB paquet(s) vulnérable(s) : $LISTE")"
  else
    record "Dépendances Maven (backend)" ABSENT "SBOM CycloneDX + osv-scanner v1.9.1" "osv-scanner indisponible (réseau / Docker)."
  fi
else
  record "Dépendances Maven (backend)" ABSENT "SBOM CycloneDX + osv-scanner v1.9.1" "SBOM non généré ou Docker absent."
fi
rm -rf "$SBOM_DIR"

# En-tête + verdict
VERDICT="🔴 PREUVES NON CONFORMES"; [ $FAIL -eq 0 ] && [ $ABSENT -gt 0 ] && VERDICT="⚪ PREUVES INCOMPLÈTES"
[ $FAIL -eq 0 ] && [ $ABSENT -eq 0 ] && VERDICT="🟢 PREUVES COMPLÈTES ET CONFORMES"
{ printf '# 🧾 Preuves machine — %s\n\n' "$(date '+%F %T')"
  printf '> Généré par `./orchestrator.sh evidence` (audit/collect_evidence.sh). Ne pas modifier à la main.\n>\n'
  for d in . backend frontend; do
    printf '> `%s` : %s@%s (%s fichier(s) non commité(s))  \n' "$d" "$(git -C "$d" branch --show-current)" \
      "$(git -C "$d" rev-parse --short HEAD)" "$(git -C "$d" status --porcelain | wc -l)"; done
  printf '>\n> **Bilan : %s PASS · %s FAIL · %s ABSENT → %s**\n\n' "$PASS" "$FAIL" "$ABSENT" "$VERDICT"
  cat "$BODY"; } > "$OUT"
rm -f "$BODY"
echo "$VERDICT ($PASS PASS · $FAIL FAIL · $ABSENT ABSENT) → $OUT"
[ $FAIL -eq 0 ] && [ $ABSENT -eq 0 ]
