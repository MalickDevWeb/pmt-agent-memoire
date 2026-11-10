#!/usr/bin/env python3
"""
Générateur de rapport de supervision Kasongo (Agent 00).

Usage :
  python3 audit/kasongo_report.py <agent_nn> [--ticket ID] [--base main] [--out docs/supervision/SUP-XXX.md]
  ./orchestrator.sh kasongo <agent_nn> [--ticket ID] [--base main]

Pour chaque livraison d'agent, ce script :
  1. Vérifie les prérequis mécaniques (check_handover.py).
  2. Vérifie les règles de code (check_agent_rules.py) si pertinent.
  3. Évalue les critères de « Fini » (DoD) de la fiche : fichiers attendus, preuves, verdicts.
  4. Génère docs/supervision/SUP-<ticket>.md avec le tableau de verdict Kasongo.
  5. (Optionnel) Ajoute un message de clôture dans agent_messages.md.

Statuts possibles :
  CONFORME     — tous les contrôles mécaniques sont verts ; Kasongo peut apposer son visa.
  INCOMPLET    — contrôles verts mais des livrables attendus sont absents.
  À REPRENDRE  — au moins un contrôle mécanique est en échec.
  ESCALADE     — anomalie de sécurité ou périmètre non autorisé.
"""
import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"
SUPERVISION_DIR = ROOT / "docs" / "supervision"
BUS_FILE = ROOT / "agent_messages.md"

# ─── Noms ───────────────────────────────────────────────────────────────────
NOMS = {
    "00": "Kasongo — Superviseur",
    "01": "Mame Diarra — Product Analyst",
    "02": "Cheikh Tidiane Diop — Software Architect",
    "03": "Ousmane Marra — Backend Developer",
    "04": "Abdoulaye — Frontend Developer",
    "05": "Aïssatou Ba — QA Engineer",
    "06": "Moussa Diallo — Code Reviewer",
    "07": "Fallou Ndiaye — DevSecOps Engineer",
    "08": "Khady Sarr — Business & Marketing",
    "09": "Ndèye Fatou Fall — Rédacteur Technique",
    "10": "Ibrahima Guèye — Release & CI/CD",
    "11": "Seynabou Cissé — Modélisation",
}

# ─── Critères de « Fini » par agent ─────────────────────────────────────────
# Chaque entrée : (description, chemin_glob_ou_None, regex_dans_contenu_ou_None)
# Si chemin absent → KO ; si regex absente dans contenu → KO.
DOD = {
    "01": [
        ("requirements.md présent et non vide",
         "docs/requirements.md", None),
        ("Pas de placeholder dans requirements.md",
         "docs/requirements.md", r"(?!.*(?:XXX|AAAAMMJJ|YYYY|\*\*))^"),
        ("Au moins une US dans docs/requirements/ ou requirements.md",
         None, None),  # vérification spéciale ci-dessous
    ],
    "02": [
        ("architecture.md présent",        "docs/architecture.md",   None),
        ("database.md présent",             "docs/database.md",        None),
        ("api-contract.md sans placeholder","docs/api-contract.md",   r"^(?!.*(?:ENDPOINT_PATH|SCHEMA_NAME|YOUR_|TODO))"),
    ],
    "03": [
        ("backend/ complet (src présent)",  "backend/src",             None),
        ("Aucune violation multi-tenant (audit-tenancy OK)", None, None),
        ("Contrat API validé (check-contract OK)",          None, None),
    ],
    "04": [
        ("frontend/src présent",            "frontend/src",            None),
        ("Aucun X-Tenant-Id côté navigateur (R3)",         None, None),
    ],
    "05": [
        ("test-report.md présent",         "docs/test-report.md",     None),
        ("QA_RESULT: PASS dans test-report","docs/test-report.md",    r"QA_RESULT\s*:\s*PASS"),
        ("Log d'exécution présent",         "logs/qa_execution.log",   None),
        ("Matrice de traçabilité dans test-report",
         "docs/test-report.md", r"(?i)matrice|traçabilité|traceability"),
    ],
    "06": [
        ("review-report.md présent",        "docs/review-report.md",   None),
        ("Verdict APPROVED dans review-report",
         "docs/review-report.md", r"VERDICT\s*:\s*APPROVED"),
        ("Fichier de preuves cité",         "docs/review-report.md",   r"evidence-\d{8}-\d{6}"),
    ],
    "07": [
        ("devsecops-pipeline.md présent",   "docs/devsecops-pipeline.md", None),
        ("VERDICT DevSecOps GO ou READY",
         "docs/devsecops-pipeline.md", r"VERDICT\s+DEVSECOPS\s*:\s*(GO|READY)"),
        ("Au moins un fichier de preuves",  None, None),  # vérification spéciale
    ],
    "08": [
        ("Au moins un livrable BIZ dans docs/business/", None, None),
        ("Section Points à valider dans le livrable",    None, None),
    ],
    "09": [
        ("memoire/docs/main.tex ou section rédigée", None, None),
        ("Journal d'IA à jour (docs/ ou memoire/)",  None, None),
    ],
    "10": [
        (".github/workflows/ci.yml ou pipeline CI présent", None, None),
        ("Rapport de livraison présent (release-notes-*.md)", None, None),
    ],
    "11": [
        ("docs/diagrams/ non vide",          None, None),
        ("gen_diagrams.py --check OK",       None, None),
    ],
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def run_py(script_rel, *args):
    """Lance un script Python de audit/ ; renvoie (code_retour, stdout+stderr)."""
    script = ROOT / script_rel
    r = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    return r.returncode, (r.stdout + r.stderr).strip()


def check_path(rel):
    """Teste si un chemin (fichier ou dossier) existe et n'est pas vide."""
    p = ROOT / rel
    if not p.exists():
        return False
    if p.is_dir():
        return any(True for _ in p.iterdir())
    return p.stat().st_size > 0


def check_regex(rel, pattern):
    """Teste si un fichier contient le pattern (re.search)."""
    p = ROOT / rel
    if not p.exists():
        return False
    try:
        content = p.read_text(encoding="utf-8", errors="ignore")
        return bool(re.search(pattern, content, re.M))
    except OSError:
        return False


def evidence_files():
    return sorted((ROOT / "docs" / "evidence").glob("evidence-*.md"))


def biz_files():
    d = ROOT / "docs" / "business"
    return sorted(d.glob("BIZ-*.md")) if d.exists() else []


def ci_pipeline():
    patterns = [
        ROOT / ".github" / "workflows" / "ci.yml",
        ROOT / ".github" / "workflows" / "ci.yaml",
        ROOT / "backend" / ".github" / "workflows",
        ROOT / "frontend" / ".github" / "workflows",
    ]
    return any(p.exists() for p in patterns)


def diagrams_non_empty():
    d = ROOT / "docs" / "diagrams"
    return d.exists() and any(True for _ in d.iterdir())


def req_has_us():
    req = ROOT / "docs" / "requirements.md"
    req_dir = ROOT / "docs" / "requirements"
    text = ""
    if req.exists():
        text += req.read_text(encoding="utf-8", errors="ignore")
    if req_dir.exists():
        for f in req_dir.glob("*.md"):
            text += f.read_text(encoding="utf-8", errors="ignore")
    return bool(re.search(r"\bUS-\d+\b", text))


def ai_journal_exists():
    for pat in ["docs/guides/journal*", "memoire/journal*", "docs/journal*"]:
        if list(ROOT.glob(pat)):
            return True
    if (ROOT / "memoire").exists():
        for f in (ROOT / "memoire").rglob("*journal*"):
            return True
    return False


def release_notes_exist():
    return bool(list(ROOT.glob("docs/release-notes-*.md")))


# ─── Évaluation des DoD par agent ────────────────────────────────────────────

def evaluate_dod(agent):
    """Renvoie [(description, bool_ok, detail)] pour chaque critère DoD."""
    items = DOD.get(agent, [])
    results = []

    for desc, path_rel, pattern in items:
        # Vérifications spéciales (path_rel=None, pattern=None)
        if path_rel is None and pattern is None:
            if agent == "01" and "US" in desc:
                ok = req_has_us()
                results.append((desc, ok, "US trouvées" if ok else "Aucune US-xx dans requirements"))
            elif agent == "03" and "multi-tenant" in desc:
                code, out = run_py("check_multi_tenancy.py")
                ok = code == 0
                summary = out.splitlines()[-1] if out else "pas de sortie"
                results.append((desc, ok, summary))
            elif agent == "03" and "contrat" in desc.lower():
                code, out = run_py("validate_contracts.py")
                ok = code == 0
                summary = out.splitlines()[-1] if out else "pas de sortie"
                results.append((desc, ok, summary))
            elif agent == "04" and "X-Tenant" in desc:
                code, out = run_py("audit/check_agent_rules.py")
                ok = "X-Tenant-Id" not in out or "✔" in out
                results.append((desc, ok, "voir check-agents"))
            elif agent == "07" and "preuves" in desc.lower():
                evs = evidence_files()
                ok = len(evs) > 0
                results.append((desc, ok, f"{len(evs)} fichier(s) de preuves" if ok else "Aucun fichier evidence-*.md"))
            elif agent == "08" and "BIZ" in desc:
                bizs = biz_files()
                ok = len(bizs) > 0
                results.append((desc, ok, f"{len(bizs)} livrable(s) BIZ" if ok else "Aucun BIZ-*.md"))
            elif agent == "08" and "valider" in desc.lower():
                ok = any(
                    re.search(r"Points à valider", f.read_text(encoding="utf-8", errors="ignore"), re.I)
                    for f in biz_files()
                ) if biz_files() else False
                results.append((desc, ok, "section trouvée" if ok else "section absente dans les livrables BIZ"))
            elif agent == "09" and "main.tex" in desc:
                ok = (ROOT / "memoire" / "docs" / "main.tex").exists() or (ROOT / "memoire").exists()
                results.append((desc, ok, "memoire/ présent" if ok else "memoire/ absent"))
            elif agent == "09" and "journal" in desc.lower():
                ok = ai_journal_exists()
                results.append((desc, ok, "journal trouvé" if ok else "Journal d'IA introuvable"))
            elif agent == "10" and "ci.yml" in desc.lower():
                ok = ci_pipeline()
                results.append((desc, ok, "pipeline CI trouvé" if ok else "Aucun .github/workflows/ci.yml"))
            elif agent == "10" and "release" in desc.lower():
                ok = release_notes_exist()
                results.append((desc, ok, "release-notes trouvé" if ok else "Aucun docs/release-notes-*.md"))
            elif agent == "11" and "diagrams" in desc.lower():
                ok = diagrams_non_empty()
                results.append((desc, ok, "docs/diagrams/ non vide" if ok else "docs/diagrams/ vide ou absent"))
            elif agent == "11" and "gen_diagrams" in desc.lower():
                code, out = run_py("audit/gen_diagrams.py", "--check")
                ok = code == 0
                summary = out.splitlines()[-1] if out else "pas de sortie"
                results.append((desc, ok, summary))
            else:
                results.append((desc, False, "vérification non implémentée"))
            continue

        # Vérification existence du chemin
        if path_rel and not check_path(path_rel):
            results.append((desc, False, f"{path_rel} absent ou vide"))
            continue

        # Vérification regex dans le contenu
        if pattern:
            ok = check_regex(path_rel, pattern)
            results.append((desc, ok, "pattern trouvé" if ok else f"pattern absent dans {path_rel}"))
        else:
            results.append((desc, True, f"{path_rel} présent"))

    return results


# ─── Génération du rapport ────────────────────────────────────────────────────

def generate_report(agent, ticket, handover_code, handover_out, rules_code, rules_out, dod_results):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    agent_name = NOMS.get(agent, f"Agent {agent}")

    # Détermination du statut global
    has_security = "ESCALADE" in handover_out or "périmètre" in handover_out.lower()
    has_handover_fail = handover_code != 0
    dod_ok = all(ok for _, ok, _ in dod_results)
    rules_ok = rules_code == 0 or rules_code is None

    if has_security:
        status = "🔴 ESCALADE"
        status_detail = "Anomalie de sécurité ou périmètre non autorisé détectée."
    elif has_handover_fail:
        status = "🟡 À REPRENDRE"
        status_detail = "Au moins un contrôle mécanique est en échec."
    elif not dod_ok:
        status = "🟠 INCOMPLET"
        status_detail = "Contrôles mécaniques verts, mais des livrables attendus sont absents."
    else:
        status = "🟢 CONFORME"
        status_detail = "Tous les contrôles mécaniques et les livrables DoD sont conformes."

    ticket_line = f" `{ticket}`" if ticket else ""

    lines = [
        f"# Rapport de Supervision Kasongo — Agent {agent}",
        f"",
        f"**Agent :** {agent_name}  ",
        f"**Ticket :**{ticket_line if ticket else ' —'}  ",
        f"**Date :** {now}  ",
        f"**Branche courante :** (voir `git branch --show-current`)  ",
        f"",
        f"---",
        f"",
        f"## Verdict Global",
        f"",
        f"| Statut | Explication |",
        f"|--------|-------------|",
        f"| **{status}** | {status_detail} |",
        f"",
        f"---",
        f"",
        f"## 1. Contrôle Mécanique (check_handover.py)",
        f"",
        f"```",
        handover_out if handover_out else "(aucune sortie)",
        f"```",
        f"",
        f"**Code de retour :** {handover_code} ({'✔ CONFORME' if handover_code == 0 else '✖ ÉCHEC'})",
        f"",
        f"---",
        f"",
    ]

    if rules_out is not None:
        lines += [
            f"## 2. Règles Vérifiables du Code (check_agent_rules.py)",
            f"",
            f"```",
            rules_out if rules_out else "(aucune sortie)",
            f"```",
            f"",
            f"**Code de retour :** {rules_code} ({'✔' if rules_code == 0 else '✖'})",
            f"",
            f"---",
            f"",
        ]

    lines += [
        f"## {'3' if rules_out is not None else '2'}. Critères de « Fini » (Definition of Done)",
        f"",
        f"| # | Critère | Statut | Détail |",
        f"|---|---------|--------|--------|",
    ]

    for i, (desc, ok, detail) in enumerate(dod_results, 1):
        icon = "✅" if ok else "❌"
        lines.append(f"| {i} | {desc} | {icon} | {detail} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## Décision Kasongo",
        f"",
        f"> ⚠️ **Ce rapport est automatique.** Le jugement qualitatif (qualité du code, pertinence métier,",
        f"> respect des scénarios Gherkin) appartient à Kasongo et/ou au Tech Lead humain.",
        f"",
        f"- **Kasongo (Agent 00) :** `[ ]` Visa apposé le ____  par ______________",
        f"- **Tech Lead humain :** `[ ]` Validé le ____ par ______________",
        f"",
        f"### Points à régler avant validation",
        f"",
    ]

    failing = [(d, det) for d, ok, det in dod_results if not ok]
    if has_handover_fail:
        failing.insert(0, ("Contrôle handover en échec", "voir section 1"))
    if failing:
        for desc, detail in failing:
            lines.append(f"- [ ] {desc} — {detail}")
    else:
        lines.append("*Aucun point bloquant identifié automatiquement.*")

    lines += [
        f"",
        f"---",
        f"*Généré par `audit/kasongo_report.py` — École 221*",
    ]

    return "\n".join(lines)


# ─── Écriture dans agent_messages.md ─────────────────────────────────────────

def append_bus_message(ticket, agent, status_global):
    if not ticket:
        return
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    agent_name = NOMS.get(agent, f"Agent {agent}")
    sup_file = f"docs/supervision/SUP-{ticket}.md"
    msg = f"""
### [SUP-{ticket}] Rapport Kasongo — Agent {agent}
- **De :** Kasongo (Agent 00)
- **À :** Tech Lead humain
- **Date :** {now}
- **Statut :** {status_global}
- **Rapport :** [{sup_file}]({sup_file})
- **Agent évalué :** {agent_name}

"""
    bus = BUS_FILE
    if bus.exists():
        content = bus.read_text(encoding="utf-8")
        # Insertion après le premier ## (section Messages de Kasongo si elle existe)
        if "## 🕵️" in content or "## Kasongo" in content:
            content += msg
        else:
            content += msg
        bus.write_text(content, encoding="utf-8")
        print(f"✔ Message [SUP-{ticket}] ajouté dans agent_messages.md")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Rapport Kasongo pour une livraison d'agent")
    parser.add_argument("agent", help="Numéro de l'agent (ex: 03)")
    parser.add_argument("--ticket", help="Identifiant du ticket (ex: FEAT-005)")
    parser.add_argument("--base", default="main", help="Branche de base pour check_handover (défaut: main)")
    parser.add_argument("--out", help="Fichier de sortie (défaut: docs/supervision/SUP-<ticket>.md)")
    parser.add_argument("--no-bus", action="store_true", help="Ne pas écrire dans agent_messages.md")
    args = parser.parse_args()

    agent = args.agent.zfill(2)

    if agent not in NOMS:
        print(f"❌ Agent inconnu : {agent}. Agents valides : {', '.join(sorted(NOMS.keys()))}")
        sys.exit(2)

    SUPERVISION_DIR.mkdir(parents=True, exist_ok=True)

    print(f"🔍 Rapport Kasongo — Agent {agent} ({NOMS[agent]})")
    print(f"   Ticket : {args.ticket or '—'}  |  Base : {args.base}")
    print()

    # 1. check_handover.py
    handover_args = [agent, "--base", args.base]
    if args.ticket:
        handover_args += ["--ticket", args.ticket]
    print("── 1. check_handover.py ──────────────────────────")
    h_code, h_out = run_py("audit/check_handover.py", *handover_args)
    print(h_out)
    print()

    # 2. check_agent_rules.py (utile pour agents 03/04)
    r_code, r_out = None, None
    if agent in ("03", "04"):
        print("── 2. check_agent_rules.py ───────────────────────")
        r_code, r_out = run_py("audit/check_agent_rules.py")
        print(r_out)
        print()

    # 3. DoD
    print("── 3. Critères de « Fini » ───────────────────────")
    dod_results = evaluate_dod(agent)
    for desc, ok, detail in dod_results:
        icon = "✅" if ok else "❌"
        print(f"  {icon} {desc}")
        if not ok:
            print(f"       → {detail}")
    print()

    # Détermination statut global
    has_security = "ESCALADE" in h_out or "périmètre" in h_out.lower()
    has_handover_fail = h_code != 0
    dod_ok = all(ok for _, ok, _ in dod_results)

    if has_security:
        status = "ESCALADE"
    elif has_handover_fail:
        status = "À REPRENDRE"
    elif not dod_ok:
        status = "INCOMPLET"
    else:
        status = "CONFORME"

    print(f"══ VERDICT : {status} ════════════════════════════")
    print()

    # Génération du rapport Markdown
    report_md = generate_report(agent, args.ticket, h_code, h_out, r_code, r_out, dod_results)

    if args.out:
        out_path = Path(args.out)
    elif args.ticket:
        out_path = SUPERVISION_DIR / f"SUP-{args.ticket}.md"
    else:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = SUPERVISION_DIR / f"SUP-{agent}-{stamp}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_md, encoding="utf-8")
    print(f"✔ Rapport écrit : {out_path.relative_to(ROOT)}")

    # Ajout dans le bus
    if not args.no_bus and args.ticket:
        append_bus_message(args.ticket, agent, status)

    return 0 if status == "CONFORME" else 1


if __name__ == "__main__":
    sys.exit(main())
