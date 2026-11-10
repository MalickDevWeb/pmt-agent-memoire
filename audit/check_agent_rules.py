#!/usr/bin/env python3
"""
Règles des fiches d'agents ↔ réalité du dépôt.

Une fiche « Conforme » ne prouve rien : ce script vérifie que ce que les fiches IMPOSENT ou
CITENT existe vraiment (fichiers, commandes) et que le code respecte les règles vérifiables.
Deux statuts de règle (cf. section « État actuel vs cible » de la fiche 04) :
  - bloquante : toute violation échoue ;
  - cible (cliquet) : échoue seulement si la mesure se dégrade par rapport à
    audit/agent_rules_baseline.json. '--update-baseline' n'enregistre que les améliorations.
Sortie : une ligne par règle (✔ respectée / ◐ cible tenue / ✖ échec) ; code 1 si au moins un échec.
Utilisé par audit/collect_evidence.sh et './orchestrator.sh check-agents'.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = sorted((ROOT / "agents").glob("*.md"))
FRONT_SRC = ROOT / "frontend" / "src"
BASELINE = ROOT / "audit" / "agent_rules_baseline.json"
TEMPLATE = re.compile(r"XXX|AAAAMMJJ|YYYY|\*")


def agent_text():
    return {p.name[:2]: p.read_text(encoding="utf-8") for p in AGENTS}


def cited_by(texts, needle):
    return ",".join(k for k, t in texts.items() if needle in t) or "-"


def front_files():
    return [p for p in FRONT_SRC.rglob("*") if p.suffix in (".ts", ".tsx")] if FRONT_SRC.exists() else []


def code_lines(path):
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if not line.lstrip().startswith(("//", "*", "/*")):
            yield n, line


def ratchet(results, measures, baseline, key, value, name, detail):
    """Règle cible : ◐ si value <= référence, ✖ si elle se dégrade, ✔ si la cible (0) est atteinte."""
    measures[key] = value
    ref = baseline.get(key)
    if value == 0:
        results.append(("ok", name, detail))
    elif ref is None or value > ref:
        results.append(("fail", name, f"{detail} — " + ("aucune référence enregistrée (--update-baseline)" if ref is None else f"dégradation : référence {ref}")))
    else:
        results.append(("cible", name, f"{detail} — cible (cliquet), référence {ref}"))


def rules(texts, baseline=None, measures=None):
    baseline = baseline or {}
    measures = {} if measures is None else measures
    results = []

    # R1 — fichiers cités par les fiches (hors modèles XXX / AAAAMMJJ)
    cited = set()
    for text in texts.values():
        cited |= set(re.findall(r"(?:docs|agents|backend|frontend|qa|ops|audit)/[A-Za-z0-9_./-]+\.(?:md|ya?ml|sh|py|json)", text))
    missing = sorted(c for c in cited if not TEMPLATE.search(c) and not (ROOT / c).exists())
    results.append(("ok" if not missing else "fail", "Fichiers cités par les fiches présents",
                    "absents : " + ", ".join(f"{m} (fiches {cited_by(texts, m)})" for m in missing) if missing else f"{len(cited)} cités"))

    # R2 — commandes ./orchestrator.sh citées
    orch = (ROOT / "orchestrator.sh").read_text(encoding="utf-8")
    known = set(re.findall(r"^\s+([a-z][a-z-]*)\)\s*$", orch, re.M))
    cmds = sorted({c for t in texts.values() for c in re.findall(r"orchestrator\.sh ([a-z][a-z-]+)", t)})
    unknown = [c for c in cmds if c not in known]
    results.append(("ok" if not unknown else "fail", "Commandes ./orchestrator.sh citées existantes",
                    "inexistantes : " + ", ".join(f"{c} (fiches {cited_by(texts, 'orchestrator.sh ' + c)})" for c in unknown)
                    if unknown else f"{len(cmds)} citées"))

    # R2b — skills d'outils IA (.agents/skills) : simple renvoi vers une fiche, aucun ordre automatique
    bad = []
    skills = sorted((ROOT / ".agents" / "skills").glob("*/SKILL.md"))
    for skill in skills:
        text = skill.read_text(encoding="utf-8")
        refs = re.findall(r"agents/(0\d_[a-z_]+\.md)", text)
        if not refs or any(not (ROOT / "agents" / r).exists() for r in refs):
            bad.append(f"{skill.parent.name} (aucun renvoi valide vers agents/)")
        if re.search(r"IMMEDIATELY|IMMÉDIATEMENT et AUTOMATIQUEMENT|SANS attendre d'instruction|"
                     r"Ne jamais demander confirmation", text, re.I):
            bad.append(f"{skill.parent.name} (ordre d'exécution automatique)")
    results.append(("ok" if not bad else "fail", "Skills .agents/ alignées sur les fiches",
                    ", ".join(bad) if bad else ("renvoi vers les fiches, pas d'exécution automatique" if skills
                                                 else "aucune skill : agents/ est la source unique")))

    files = front_files()
    pkg = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    # R3 — fiche 04 : aucun en-tête X-Tenant-Id envoyé par le navigateur
    hits = [f"{p.relative_to(ROOT)}:{n}" for p in files for n, l in code_lines(p) if re.search(r"X-Tenant-I[dD]", l)]
    results.append(("ok" if not hits else "fail", "[04] Aucun en-tête X-Tenant-Id envoyé par le frontend", ", ".join(hits[:5]) or "aucun"))

    # R4 — fiche 04 : formulaires react-hook-form + zod
    absent = [d for d in ("zod", "react-hook-form", "@hookform/resolvers") if d not in deps]
    measures["forms_packages_installed"] = not absent
    name = "[04] react-hook-form + zod installés"
    if not absent:
        results.append(("ok", name, "ok"))
    elif baseline.get("forms_packages_installed"):
        results.append(("fail", name, "manquants : " + ", ".join(absent) + " — régression : ils étaient installés"))
    else:
        results.append(("cible", name, "manquants : " + ", ".join(absent) + " — cible, installation à décider par le Tech Lead"))

    # R5 — fiche 04 : appels API via React Query
    src = {p: p.read_text(encoding="utf-8", errors="ignore") for p in files}
    rq = sum(1 for t in src.values() if re.search(r"\buse(Query|Mutation)\(", t))
    direct = sum(1 for t in src.values() if "apiClient." in t and not re.search(r"\buse(Query|Mutation)\(", t))
    ratchet(results, measures, baseline, "api_files_without_react_query", direct,
            "[04] Appels API via React Query", f"{direct} fichier(s) appellent apiClient sans React Query, {rq} l'utilisent")

    # R6 — fiche 04 : TypeScript strict, aucun any
    anys = {}
    for p in files:
        n = sum(len(re.findall(r":\s*any\b|<any>|\bas any\b|\bany\[\]", l)) for _, l in code_lines(p))
        if n:
            anys[str(p.relative_to(ROOT))] = n
    top = ", ".join(f"{f} ({n})" for f, n in sorted(anys.items(), key=lambda x: -x[1])[:3])
    ratchet(results, measures, baseline, "typescript_any", sum(anys.values()), "[04] Aucun type any",
            f"{sum(anys.values())} any dans {len(anys)} fichier(s) — max : {top}" if anys else "0")

    # R7 — fiche 01 : requirements.md présent, non vide, au moins une US-xx
    req = ROOT / "docs" / "requirements.md"
    req_dir = ROOT / "docs" / "requirements"
    req_text = ""
    if req.exists():
        req_text += req.read_text(encoding="utf-8", errors="ignore")
    if req_dir.exists():
        for f in sorted(req_dir.glob("*.md")):
            req_text += f.read_text(encoding="utf-8", errors="ignore")
    has_us = bool(re.search(r"\bUS-\d+\b", req_text))
    has_req = req.exists() and req.stat().st_size > 100
    results.append(("ok" if (has_req and has_us) else "fail",
                    "[01] requirements.md présent et contient des US-xx",
                    "OK" if (has_req and has_us) else
                    ("requirements.md absent ou vide" if not has_req else "Aucune US-xx trouvée")))

    # R8 — fiche 02 : api-contract.md sans placeholder XXX/ENDPOINT_PATH/TODO
    contract = ROOT / "docs" / "api-contract.md"
    PLACEHOLDER_CONTRACT = re.compile(r"ENDPOINT_PATH|SCHEMA_NAME|YOUR_|TODO|XXX|AAAAMMJJ")
    if contract.exists():
        ct = contract.read_text(encoding="utf-8", errors="ignore")
        ph = PLACEHOLDER_CONTRACT.findall(ct)
        results.append(("ok" if not ph else "fail",
                        "[02] api-contract.md sans placeholder non rempli",
                        f"{len(ph)} placeholder(s) détecté(s)" if ph else "OK"))
    else:
        results.append(("fail", "[02] api-contract.md présent", "docs/api-contract.md absent"))

    # R9 — fiche 05 : logs/qa_execution.log a QA_RESULT: PASS
    qa_log = ROOT / "logs" / "qa_execution.log"
    if qa_log.exists():
        qa_text = qa_log.read_text(encoding="utf-8", errors="ignore")
        qa_pass = bool(re.search(r"QA_RESULT\s*:\s*PASS", qa_text))
        results.append(("ok" if qa_pass else "fail",
                        "[05] logs/qa_execution.log contient QA_RESULT: PASS",
                        "PASS trouvé" if qa_pass else "QA_RESULT: PASS absent — le QA n'est pas vert"))
    else:
        results.append(("fail", "[05] logs/qa_execution.log présent",
                        "logs/qa_execution.log absent — le QA n'a pas été exécuté"))

    # R10 — fiche 06 : review-report.md a VERDICT: APPROVED
    review = ROOT / "docs" / "review-report.md"
    if review.exists():
        rv = review.read_text(encoding="utf-8", errors="ignore")
        approved = bool(re.search(r"VERDICT\s*:\s*APPROVED", rv))
        results.append(("ok" if approved else "fail",
                        "[06] review-report.md contient VERDICT: APPROVED",
                        "APPROVED trouvé" if approved else "Pas de VERDICT: APPROVED — revue non approuvée"))
    else:
        results.append(("fail", "[06] review-report.md présent", "docs/review-report.md absent"))

    # R11 — fiche 07 : au moins un fichier de preuves récent (docs/evidence/)
    evidence_dir = ROOT / "docs" / "evidence"
    ev_files = sorted(evidence_dir.glob("evidence-*.md")) if evidence_dir.exists() else []
    results.append(("ok" if ev_files else "fail",
                    "[07] Au moins un fichier de preuves docs/evidence/evidence-*.md",
                    f"{len(ev_files)} fichier(s)" if ev_files else "Aucun fichier evidence-*.md"))

    return results


def load_baseline():
    try:
        return json.loads(BASELINE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def update_baseline(baseline, measures):
    """N'enregistre que les améliorations : un compteur ne remonte jamais, un paquet installé le reste."""
    new = dict(baseline)
    for key, value in measures.items():
        if isinstance(value, bool):
            new[key] = bool(baseline.get(key)) or value
        else:
            new[key] = value if key not in baseline else min(baseline[key], value)
    BASELINE.write_text(json.dumps(new, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return new


ICON = {"ok": "✔", "cible": "◐", "fail": "✖"}


def main(argv):
    baseline, measures = load_baseline(), {}
    results = rules(agent_text(), baseline, measures)
    for status, name, detail in results:
        print(f"{ICON[status]} {name} — {detail}")
    count = {k: sum(1 for st, _, _ in results if st == k) for k in ICON}
    print(f"Bilan : {count['ok']} règle(s) respectée(s), {count['cible']} cible(s) tenue(s) sans régression, "
          f"{count['fail']} en échec")
    if "--update-baseline" in argv:
        print("Référence mise à jour :", json.dumps(update_baseline(baseline, measures), sort_keys=True))
    return 1 if count["fail"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
