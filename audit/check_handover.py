#!/usr/bin/env python3
"""
Contrôle automatique d'une livraison d'agent — utilisé par Kasongo (Agent 00, Superviseur).

  python3 audit/check_handover.py <agent> [--ticket ID] [--base main] [--only racine|backend|frontend]
  ./orchestrator.sh handover <agent> [--ticket ID] [--base main] [--only …]

Vérifie, sur les commits de la branche courante depuis --base (dépôts racine, backend et frontend) :
  1. Périmètre   : chaque fichier modifié est autorisé pour cet agent (matrice PERIMETRES).
  2. Secrets     : aucune ligne ajoutée ne ressemble à un secret (mot de passe, token, clé, URL avec identifiants).
  3. Bus         : avec --ticket, le message existe dans agent_messages.md avec un statut.
Code de sortie 0 = contrôles automatiques conformes ; 1 = non conforme ; 2 = usage.
Le jugement sur la qualité (définition de « fini » de la fiche) reste celui de Kasongo, APRÈS ce script.
"""
import argparse
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPOS = {"": ROOT, "backend/": ROOT / "backend", "frontend/": ROOT / "frontend"}
BUS = "agent_messages.md"

# (autorisé, interdit) — chemins relatifs à la racine du projet. L'interdit l'emporte.
# Fichiers de gouvernance (agents/, orchestrator.sh, audit/, tests/) : Tech Lead humain uniquement.
PERIMETRES = {
    "00": ([BUS, "docs/supervision/*"], []),
    "01": ([BUS, "docs/requirements.md", "docs/requirements/*"], []),
    "02": ([BUS, "docs/api-contract.md", "docs/architecture.md", "docs/database.md"], []),
    "03": ([BUS, "backend/*", "backend_history.md"],
           ["backend/Dockerfile", "backend/.github/*", "backend/render.yaml", "backend/.env", "backend/.env.*[!e]"]),
    "04": ([BUS, "frontend/*", "frontend_history.md"],
           ["frontend/Dockerfile", "frontend/nginx.conf", "frontend/.github/*", "frontend/.env", "frontend/.env.*[!e]",
            "frontend/package.json", "frontend/package-lock.json"]),
    "05": ([BUS, "test_*.sh", "lib_http_assert.sh", "run_all_integration_tests.sh", "qa/*", "logs/*",
            "docs/test-report.md", "docs/qa/*"], []),
    "06": ([BUS, "docs/review-report.md", "docs/evidence/*"], []),
    "07": ([BUS, "docs/devsecops-pipeline.md", "docs/evidence/*", "docker-compose.yml",
            "backend/Dockerfile", "frontend/Dockerfile", "frontend/nginx.conf", ".gitleaksignore"], []),
    "08": ([BUS, "docs/business/*"], []),
    "09": ([BUS, "memoire/*", "docs/guides/*"], ["memoire/**/.env*"]),
    "10": ([BUS, ".github/workflows/*", "backend/.github/workflows/*", "frontend/.github/workflows/*",
            "docs/release-notes-*.md", "backend/render.yaml"], []),
    "11": ([BUS, "docs/diagrams/*"], []),
}
NOMS = {"00": "Kasongo — Superviseur", "01": "Mame Diarra — Product Analyst",
        "02": "Cheikh Tidiane Diop — Software Architect", "03": "Ousmane Marra — Backend Developer",
        "04": "Abdoulaye — Frontend Developer", "05": "Aïssatou Ba — QA Engineer",
        "06": "Moussa Diallo — Code Reviewer", "07": "Fallou Ndiaye — DevSecOps Engineer",
        "08": "Khady Sarr — Business & Marketing", "09": "Ndèye Fatou Fall — Rédacteur technique",
        "10": "Ibrahima Guèye — Release & CI/CD", "11": "Seynabou Cissé — Modélisation"}
KEYWORD = r"(?:password|passwd|secret|api[_-]?key|token|private[_-]?key)"
SECRET = re.compile(
    rf"""(?ix)
    {KEYWORD}\w*["']?\s*[:=]\s*(["'])(?P<quoted>[^"'\s]{{8,}})\1      # littéral entre guillemets
    | ^\s*[\w.-]*{KEYWORD}\w*\s*[:=]\s*(?P<bare>[^\s"'$<{{#();]{{8,}})\s*$  # valeur nue (.env, yaml)
    | \b[a-z]+://[^\s/:@]+:[^\s/@$<{{]{{6,}}@                          # URL avec identifiants
    | eyJ[A-Za-z0-9_-]{{20,}}\.[A-Za-z0-9_-]{{20,}}                       # JWT
    | -----BEGIN\ [A-Z\ ]*PRIVATE\ KEY-----
    """)
PLACEHOLDER = re.compile(r"(?i)change[-_]?me|your[-_]|example|exemple|xxx|<.*>|\*\*\*|dummy|placeholder|test[-_]?only")


def is_secret(line):
    m = SECRET.search(line)
    if not m:
        return False
    value = m.group("quoted") or m.group("bare") or m.group(0)
    return not PLACEHOLDER.search(value)


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def changes(base, only=None):
    """[(chemin depuis la racine, lignes ajoutées)] des commits depuis base, pour chaque dépôt."""
    out, missing = [], []
    for prefix, repo in REPOS.items():
        if only and (prefix.rstrip("/") or "racine") != only:
            continue
        if not (repo / ".git").exists():
            continue
        if git(repo, "rev-parse", "--verify", "-q", base) is None:
            missing.append(prefix or "racine")
            continue
        names = git(repo, "diff", "--name-only", f"{base}...HEAD") or ""
        for name in filter(None, names.splitlines()):
            if prefix == "" and name in ("backend", "frontend"):
                continue  # pointeurs de sous-dépôts : leur contenu est contrôlé dans leur propre dépôt
            patch = git(repo, "diff", f"{base}...HEAD", "--", name) or ""
            added = [l[1:] for l in patch.splitlines() if l.startswith("+") and not l.startswith("+++")]
            out.append((prefix + name, added))
    return out, missing


def allowed(agent, path):
    ok, ko = PERIMETRES[agent]
    match = lambda pats: any(fnmatch.fnmatch(path, p) for p in pats)  # noqa: E731
    return match(ok) and not match(ko)


def ticket_status(ticket):
    bus = ROOT / BUS
    if not bus.exists():
        return None
    text = bus.read_text(encoding="utf-8")
    m = re.search(rf"^###\s*\[{re.escape(ticket)}\].*?(?=^###\s*\[|^##\s|\Z)", text, re.S | re.M)
    if not m:
        return None
    s = re.search(r"Stat(?:us|ut)\W+([A-Z_]+)", m.group(0))
    return s.group(1) if s else "SANS_STATUT"


def check(agent, base, ticket=None, only=None):
    results = []
    files, missing = changes(base, only)
    if missing:
        results.append((False, "Base de comparaison", f"« {base} » absente dans : {', '.join(missing)}"))
    hors = [p for p, _ in files if not allowed(agent, p)]
    results.append((not hors, "Périmètre de la fiche",
                    f"hors périmètre : {', '.join(hors[:8])}" + (" …" if len(hors) > 8 else "") if hors
                    else f"{len(files)} fichier(s) modifié(s), tous autorisés"))
    leaks = [p for p, added in files for l in added if is_secret(l)]
    results.append((not leaks, "Aucun secret ajouté",
                    f"motif de secret dans : {', '.join(sorted(set(leaks))[:8])}" if leaks else "aucun motif détecté"))
    if ticket:
        st = ticket_status(ticket)
        results.append((st not in (None, "SANS_STATUT"), f"Ticket [{ticket}] dans le bus",
                        "absent" if st is None else ("sans statut" if st == "SANS_STATUT" else f"statut {st}")))
    return results


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("agent", help="numéro d'agent, ex. 03")
    ap.add_argument("--ticket")
    ap.add_argument("--base", default="main")
    ap.add_argument("--only", choices=["racine", "backend", "frontend"], help="un seul dépôt")
    a = ap.parse_args(argv)
    agent = a.agent.zfill(2)
    if agent not in PERIMETRES:
        print(f"Agent inconnu : {a.agent} (connus : {', '.join(PERIMETRES)})")
        return 2
    print(f"🔎 Livraison de l'Agent {agent} — {NOMS[agent]} (depuis {a.base})")
    results = check(agent, a.base, a.ticket, a.only)
    for ok, name, detail in results:
        print(f"{'✔' if ok else '✖'} {name} — {detail}")
    bad = sum(1 for ok, _, _ in results if not ok)
    print("CONTRÔLES AUTOMATIQUES : " + ("CONFORMES → avis de Kasongo sur la définition de « fini »"
                                         if not bad else f"NON CONFORMES ({bad}) → À REPRENDRE"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
