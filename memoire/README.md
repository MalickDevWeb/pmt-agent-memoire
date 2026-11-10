# Documentaion_des_projet

Projet isole pour produire la documentation de n'importe quel projet avec:

- LaTeX en direct dans VS Code;
- Docker / DevContainer;
- captures de code stylisees;
- captures reelles de fenetre VS Code;
- templates reutilisables (rapport, memoire).

## Objectif

Standardiser la documentation technique et academique sans dependre de la stack du projet cible.

## Structure

```text
Documentaion_des_projet/
  .devcontainer/
  .vscode/
  docs/
  scripts/
  templates/
  package.json
```

## Demarrage rapide

Mode universel recommande (Windows/Linux/macOS) avec Docker:

```bash
npm run doc:init:report
# ou
npm run doc:init:memoire
npm run doc:build
```

Mode local (si LaTeX deja installe): `npm run build`

PDF genere:
- `docs/build/main.pdf`
- lien rapide: `docs/main.pdf`

## Scripts packagiste (npm)

- `npm run doctor`: verifier l'environnement
- `npm run doc:init:report`: init template report via Docker
- `npm run doc:init:memoire`: init template memoire via Docker
- `npm run doc:build`: build PDF via Docker
- `npm run doc:watch`: watch PDF via Docker
- `npm run doc:clean`: clean via Docker
- `npm run build`: compilation PDF
- `npm run watch`: compilation continue
- `npm run clean`: nettoyage auxiliaires
- `npm run template:list`: liste templates
- `npm run template:init:report`: applique template rapport
- `npm run template:init:memoire`: applique template memoire
- `npm run capture:code -- <fichier> <debut> <fin> <sortie.png>`
- `npm run capture:vscode -- --source <fichier> --line <n> --output <png>`

## Captures

### Capture code stylisee

```bash
npm run capture:code -- src/app.ts 10 80 docs/captures/app-ts.png
```

### Capture VS Code reelle

```bash
npm run capture:vscode -- \
  --source /chemin/projet/src/app.ts \
  --line 120 \
  --output docs/captures/reelle-vscode.png
```

## Prerequis hote (Linux)

```bash
sudo apt update
sudo apt install -y wmctrl xdotool x11-utils python3-pil
```

## Reference complete

Voir le guide complet:
- `DOCUMENTATION_COMPLETE_LATEX_DOCKER_VSCODE.md`
