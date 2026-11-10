#!/usr/bin/env python3
"""
Convocation d'un agent par Kasongo (Agent 00) quand son travail est jugé « À REPRENDRE ».

  ./orchestrator.sh convoquer <NN> <TICKET> [--hors-horaires] [--simulation]

Déroulé (paramètres dans orchestration/equipe.json → "convocation") :
  1. Lecture du rapport docs/supervision/SUP-<TICKET>.md : il doit conclure « À REPRENDRE ».
  2. Convocation (au plus max_tentatives fois) : l'agent explique la cause de chaque écart, corrige ce qui
     relève de son périmètre, escalade le reste ; puis Kasongo contrôle à nouveau et réécrit son rapport.
  3. Toujours non conforme → REMPLAÇANT : nouvelle instance du même rôle (même fiche, mêmes droits), qui
     repart sans l'historique des tentatives ratées, avec une réflexion plus poussée.
  4. Échec du remplaçant → ESCALADE au Tech Lead. Rien n'est commité, fusionné ni déployé automatiquement.
Historique : logs/agent_runs/convocations.json.
"""
import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / "orchestration" / "agent_runtime.py"
HISTORY = ROOT / "logs" / "agent_runs" / "convocations.json"
VERDICT = re.compile(r"VERDICT KASONGO\W*:?\W*(CONFORME|À REPRENDRE|A REPRENDRE|ESCALADE)", re.I)


def rapport(ticket):
    p = ROOT / "docs" / "supervision" / f"SUP-{ticket}.md"
    return p.read_text(encoding="utf-8") if p.exists() else None


def verdict(text):
    m = VERDICT.findall(text or "")
    return m[-1].upper().replace("A REPRENDRE", "À REPRENDRE") if m else None


def run_agent(nn, tache, budget, effort, extra):
    argv = [sys.executable, str(RUNTIME), nn, tache, "--budget", f"{budget:.2f}", "--effort", effort, *extra]
    print(f"\n▶ {' '.join(argv[2:3])} — effort {effort}, budget ${budget:.2f}")
    return subprocess.run(argv, cwd=ROOT).returncode


def kasongo_recontrole(ticket, agent, cfg, extra):
    tache = (f"Nouveau contrôle du ticket {ticket} après convocation de l'Agent {agent}. Relis ton rapport "
             f"docs/supervision/SUP-{ticket}.md, vérifie chaque écart avec des preuves, puis RÉÉCRIS ce rapport "
             "avec une section « Contrôle après convocation » et la ligne finale exacte "
             "« VERDICT KASONGO: CONFORME | À REPRENDRE | ESCALADE ». Publie [SUP-" + ticket + "] dans le bus.")
    run_agent("00", tache, cfg["budget_kasongo"], "medium", extra)
    return verdict(rapport(ticket))


def main(argv):
    ap = argparse.ArgumentParser(description="Convocation d'un agent par Kasongo.")
    ap.add_argument("agent")
    ap.add_argument("ticket")
    ap.add_argument("--hors-horaires", action="store_true", help="dérogation du Tech Lead")
    ap.add_argument("--simulation", action="store_true", help="affiche le plan sans appeler l'API")
    a = ap.parse_args(argv)
    nn, ticket = a.agent.zfill(2), a.ticket
    if not re.fullmatch(r"[A-Z0-9-]{2,30}", ticket):
        raise SystemExit("Ticket invalide.")
    cfg = json.loads((ROOT / "orchestration" / "equipe.json").read_text(encoding="utf-8"))["convocation"]
    nom = json.loads((ROOT / "orchestration" / "equipe.json").read_text(encoding="utf-8"))["agents"][nn]["nom"]
    text = rapport(ticket)
    v = verdict(text)
    if v != "À REPRENDRE":
        print(f"Rien à faire : le rapport SUP-{ticket} conclut « {v or 'aucun verdict'} » (convocation seulement si « À REPRENDRE »).")
        return 0
    extra = ["--hors-horaires"] if a.hors_horaires else []
    plan = [f"convocation {i + 1}/{cfg['max_tentatives']} de {nom}" for i in range(cfg["max_tentatives"])]
    plan += [f"remplaçant de {nom} (effort {cfg['effort_remplacant']})", "escalade au Tech Lead si échec"]
    cout_max = (cfg["max_tentatives"] + 1) * (cfg["budget_par_tentative"] + cfg["budget_kasongo"])
    print(f"📣 Kasongo convoque {nom} (Agent {nn}) pour {ticket}. Plan : " + " → ".join(plan)
          + f". Coût maximal : ${cout_max:.2f}.")
    if a.simulation:
        return 0

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    hist = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else {}
    dossier = hist.setdefault(ticket, {"agent": nn, "etapes": []})

    def note(etape, resultat):
        dossier["etapes"].append({"t": dt.datetime.now().isoformat(timespec="seconds"), "etape": etape, "verdict": resultat})
        HISTORY.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")

    for i in range(1, cfg["max_tentatives"] + 1):
        tache = (f"CONVOCATION par Kasongo (superviseur), tentative {i}/{cfg['max_tentatives']}, ticket {ticket}.\n"
                 f"Rapport de Kasongo :\n---\n{rapport(ticket)}\n---\n"
                 "1) Pour chaque écart, explique en une ou deux phrases sa cause réelle (sans te justifier).\n"
                 "2) Corrige ce qui relève de ton périmètre, avec preuve (commande exécutée, fichier:ligne).\n"
                 "3) Ce qui ne relève pas de ton périmètre ou demande une décision humaine : statut ESCALADE.\n"
                 "4) Termine avec `terminer` en listant écart par écart : corrigé / escaladé / impossible.")
        if run_agent(nn, tache, cfg["budget_par_tentative"], "medium", extra) == 3:
            note(f"convocation {i}", "HORS_HORAIRES_OU_BUDGET")
            print("⏸  Convocation reportée (horaires ou budget du jour).")
            return 3
        v = kasongo_recontrole(ticket, nn, cfg, extra)
        note(f"convocation {i}", v)
        print(f"   ⇒ verdict de Kasongo : {v}")
        if v in ("CONFORME", "ESCALADE"):
            return 0 if v == "CONFORME" else 2

    tache = (f"Tu REMPLACES l'agent titulaire sur le ticket {ticket} : il n'a pas obtenu la conformité après "
             f"{cfg['max_tentatives']} convocations. Repars des faits, pas de son travail : lis la fiche, le livrable "
             f"et le dernier rapport de Kasongo (docs/supervision/SUP-{ticket}.md), puis livre un travail conforme "
             "à la définition de « fini ». Ce qui demande une décision humaine : statut ESCALADE.")
    run_agent(nn, tache, cfg["budget_par_tentative"], cfg["effort_remplacant"], extra)
    v = kasongo_recontrole(ticket, nn, cfg, extra)
    note("remplaçant", v)
    if v == "CONFORME":
        print(f"✔ Le remplaçant a obtenu la conformité sur {ticket}.")
        return 0
    note("escalade", "ESCALADE")
    print(f"🚨 ESCALADE : {ticket} reste non conforme après {cfg['max_tentatives']} convocations et un remplaçant. "
          f"Décision du Tech Lead requise (voir docs/supervision/SUP-{ticket}.md et {HISTORY.relative_to(ROOT)}).")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
