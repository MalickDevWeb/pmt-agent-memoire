#!/usr/bin/env python3
"""
Diagrammes « tel que construit » générés depuis le code backend (Agent 11).

  python3 audit/gen_diagrams.py            → (ré)écrit docs/diagrams/generated/*.puml
  python3 audit/gen_diagrams.py --check    → code 1 si un diagramme ne correspond plus au code
  python3 audit/gen_diagrams.py --render   → génère aussi les PNG (plantuml requis)

Produit :
  bd-<module>.puml       tables JPA (@Entity) du module : colonnes, clé, marqueur école (@TenantId)
  bd-ensemble.puml       toutes les tables et leurs liens
  classes-<module>.puml  modèle du domaine (domain/model) : attributs, méthodes métier, associations

Limites (à rappeler dans le mémoire) : analyse par expressions régulières, pas un compilateur.
Les liens entre tables sont presque tous implicites (champs « studentId », pas de @ManyToOne) :
ils sont DÉDUITS du nom de colonne et dessinés en pointillés « déduit ».
"""
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "backend" / "src" / "main" / "java"
OUT = ROOT / "docs" / "diagrams" / "generated"
HEADER = "' Généré par audit/gen_diagrams.py"
USER_ALIASES = {"student", "professor", "prof", "teacher", "user", "author", "sender", "receiver",
                "recipient", "created_by", "uploaded_by", "owner", "admin", "parent_user"}
FIELD = re.compile(r"^(?:(?:private|protected|public)\s+)?(?!static\b|return\b)(?:final\s+)?"
                   r"([\w.]+(?:<[\w<>,.?\s\[\]]*>)?(?:\[\])?)\s+(\w+)\s*(?:=[^;]*)?;\s*$")
METHOD = re.compile(r"^public\s+(static\s+)?(?!class|record|enum|interface)[\w<>,.?\s\[\]]+?\s+(\w+)\s*\(")


def module_of(path):
    parts = path.relative_to(SRC).parts
    if "modules" in parts:
        i = parts.index("modules")
        return parts[i + 1] + ("-" + parts[i + 2] if parts[i + 1] == "platform" else "")
    return "shared"


def snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def class_body(text):
    """(nom, type, lignes de profondeur 1 avec leurs annotations) de la première classe du fichier."""
    m = re.search(r"\b(class|record|enum)\s+(\w+)", text)
    if not m:
        return None, None, []
    members, depth, pending = [], 0, []
    for line in text[m.start():].splitlines():
        stripped = line.strip()
        if depth == 1 and stripped:
            annos = re.findall(r"@[\w.]+(?:\([^)]*\))?", stripped)
            rest = re.sub(r"@[\w.]+(?:\([^)]*\))?", "", stripped).strip()
            pending += annos
            if rest:
                members.append((rest, pending))
                pending = []
        depth += line.count("{") - line.count("}")
    return m.group(2), m.group(1), members


def parse_entity(path):
    text = strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
    if not re.search(r"^@Entity\b", text, re.M):
        return None
    name, _, members = class_body(text)
    t = re.search(r'@Table\s*\(\s*name\s*=\s*"([^"]+)"', text)
    table = t.group(1) if t else snake(name.replace("JpaEntity", "").replace("Entity", ""))
    columns, tenant = [], False
    for rest, annos in members:
        f = FIELD.match(rest)
        if not f or any(a.startswith("@Transient") for a in annos):
            continue
        typ, field = f.group(1), f.group(2)
        joined = " ".join(annos)
        c = re.search(r'@(?:[\w.]+\.)?(?:Column|JoinColumn)\s*\([^)]*name\s*=\s*"([^"]+)"', joined)
        col = c.group(1) if c else snake(field)
        is_tenant = "TenantId" in joined
        tenant |= is_tenant
        columns.append({"col": col, "type": typ.split(".")[-1], "pk": "@Id" in joined or "EmbeddedId" in joined,
                        "tenant": is_tenant, "assoc": re.search(r"@(?:[\w.]+\.)?(ManyToOne|OneToOne)\b", joined)})
    return {"name": name, "table": table, "columns": columns, "tenant": tenant, "module": module_of(path)}


def parse_domain(path):
    text = strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
    name, kind, members = class_body(text)
    if not name:
        return None
    fields, methods = [], []
    if kind == "record":
        r = re.search(r"record\s+\w+\s*\(([^)]*)\)", text, re.S)
        for part in filter(None, (p.strip() for p in (r.group(1) if r else "").split(","))):
            bits = part.rsplit(None, 1)
            if len(bits) == 2:
                fields.append((bits[0], bits[1]))
    for rest, _ in members:
        f = FIELD.match(rest)
        if f and "(" not in rest:
            fields.append((f.group(1), f.group(2)))
            continue
        m = METHOD.match(rest)
        if m and not re.match(r"(get|set|is)[A-Z]|equals$|hashCode$|toString$", m.group(2)) and m.group(2) != name:
            methods.append(("{static} " if m.group(1) else "") + m.group(2))
    if kind == "enum":
        body = text[text.index("{", text.index("enum")) + 1:]
        consts = re.match(r"\s*([A-Z0-9_,\s()\"'.\w-]*?)(;|})", body)
        fields = [("", c.split("(")[0].strip()) for c in (consts.group(1) if consts else "").split(",") if c.strip()]
    return {"name": name, "kind": kind, "fields": fields, "methods": sorted(set(methods)),
            "module": module_of(path)}


def link_target(col, by_key, table):
    """Table visée par une colonne « xxx_id » (déduction par le nom), ou None."""
    if not col.endswith("_id") or col in ("id", "organization_id"):
        return None
    prefix = col[:-3]
    if prefix in USER_ALIASES or prefix.endswith("_user"):
        return by_key.get("user")
    for key in (prefix, prefix.rstrip("s"), prefix.split("_")[-1]):
        target = by_key.get(key)
        if target and target != table:
            return target
    return None


def erd(entities, title, by_key, detail=True):
    lines = ["@startuml", f"title {title}", "hide circle", "skinparam linetype ortho",
             "legend right\n  « école » : colonne organization_id filtrée par Hibernate (@TenantId)\n"
             "  pointillés : lien déduit du nom de colonne (pas de clé étrangère déclarée)\nendlegend"]
    names = {e["table"] for e in entities}
    for e in sorted(entities, key=lambda x: x["table"]):
        stereo = " <<école>>" if e["tenant"] else ""
        lines.append(f'entity "{e["table"]}"{stereo} {{')
        if detail:
            for c in sorted(e["columns"], key=lambda c: (not c["pk"], c["col"])):
                mark = "* " if c["pk"] else ("# " if c["tenant"] else "  ")
                lines.append(f'  {mark}{c["col"]} : {c["type"]}')
        lines.append("}")
    links = sorted({(e["table"], t, c["col"], bool(c["assoc"])) for e in entities for c in e["columns"]
                    if (t := link_target(c["col"], by_key, e["table"]))})
    for target in sorted({t for _, t, _, _ in links} - names):
        lines.append(f'entity "{target}" <<autre module>> #EEEEEE')
    names |= {t for _, t, _, _ in links}
    seen = set()
    for e in sorted(entities, key=lambda x: x["table"]):
        for c in e["columns"]:
            target = link_target(c["col"], by_key, e["table"])
            if target and target in names and (e["table"], target, c["col"]) not in seen:
                seen.add((e["table"], target, c["col"]))
                style = "--" if c["assoc"] else ".."
                lines.append(f'"{e["table"]}" }}o{style}|| "{target}" : {c["col"]}' + ("" if c["assoc"] else " (déduit)"))
    return "\n".join(lines + ["@enduml", ""])


def class_diagram(classes, title):
    lines = ["@startuml", f"title {title}", "skinparam classAttributeIconSize 0"]
    names = {c["name"] for c in classes}
    for c in sorted(classes, key=lambda x: x["name"]):
        kw = {"enum": "enum", "record": "class"}.get(c["kind"], "class")
        stereo = " <<record>>" if c["kind"] == "record" else ""
        lines.append(f'{kw} {c["name"]}{stereo} {{')
        for typ, field in c["fields"]:
            lines.append(f"  {field}" + (f" : {typ}" if typ else ""))
        for m in c["methods"]:
            lines.append(f"  + {m}()" if not m.startswith("{static}") else f"  {{static}} + {m[9:]}()")
        lines.append("}")
    for c in sorted(classes, key=lambda x: x["name"]):
        for typ, field in c["fields"]:
            for other in sorted(names - {c["name"]}):
                if re.search(rf"\b{other}\b", typ):
                    many = re.match(r"(List|Set|Collection)<", typ)
                    lines.append(f'{c["name"]} --> "{"*" if many else "1"}" {other} : {field}')
    return "\n".join(lines + ["@enduml", ""])


def build():
    files = sorted(SRC.rglob("*.java"))
    entities = [e for e in (parse_entity(p) for p in files) if e]
    domain = [d for d in (parse_domain(p) for p in files if "/domain/model/" in str(p)) if d]
    by_key = {}
    for e in entities:
        for key in (e["table"], e["table"].rstrip("s"), snake(e["name"].replace("JpaEntity", "").replace("Entity", ""))):
            by_key.setdefault(key, e["table"])
    out = {}
    by_module = defaultdict(list)
    for e in entities:
        by_module[e["module"]].append(e)
    for mod, ents in by_module.items():
        out[f"bd-{mod}.puml"] = erd(ents, f"Base de données — module {mod} (tel que construit)", by_key)
    out["bd-ensemble.puml"] = erd(entities, f"Base de données — vue d'ensemble ({len(entities)} tables)", by_key, detail=False)
    dom_by_module = defaultdict(list)
    for d in domain:
        dom_by_module[d["module"]].append(d)
    for mod, cls in dom_by_module.items():
        out[f"classes-{mod}.puml"] = class_diagram(cls, f"Modèle du domaine — module {mod} (tel que construit)")
    return out


def strip_header(text):
    return "\n".join(l for l in text.splitlines() if not l.startswith(HEADER))


def main(argv):
    try:
        sha = subprocess.run(["git", "-C", str(ROOT / "backend"), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sha = "inconnu"
    wanted = {name: f"{HEADER} depuis backend@{sha} — ne pas modifier à la main\n" + body
              for name, body in build().items()}
    if "--check" in argv:
        existing = {p.name: p.read_text(encoding="utf-8") for p in OUT.glob("*.puml")} if OUT.exists() else {}
        drift = sorted(n for n in wanted if n not in existing or strip_header(existing[n]) != strip_header(wanted[n]))
        extra = sorted(set(existing) - set(wanted))
        for n in drift:
            print(f"✖ {n} ne correspond plus au code (ou absent)")
        for n in extra:
            print(f"✖ {n} ne correspond plus à aucun module")
        print(f"Bilan : {len(wanted) - len(drift)}/{len(wanted)} diagramme(s) à jour" + (f", {len(extra)} en trop" if extra else ""))
        return 1 if drift or extra else 0
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.puml"):
        if old.name not in wanted:
            old.unlink()
    for name, body in wanted.items():
        (OUT / name).write_text(body, encoding="utf-8")
    print(f"✔ {len(wanted)} diagramme(s) écrits dans {OUT.relative_to(ROOT)} (backend@{sha})")
    if "--render" in argv:
        png = OUT / "png"
        png.mkdir(exist_ok=True)
        r = subprocess.run(["plantuml", "-tpng", "-o", str(png), *map(str, sorted(OUT.glob("*.puml")))],
                           capture_output=True, text=True)
        print(("✔ PNG dans " if r.returncode == 0 else "✖ plantuml a échoué : " + r.stderr[-500:] + " ") + str(png.relative_to(ROOT)))
        return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
