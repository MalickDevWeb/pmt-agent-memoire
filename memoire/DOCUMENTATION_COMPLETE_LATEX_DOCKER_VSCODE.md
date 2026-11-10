# Documentation complète: LaTeX + Docker + VS Code + captures (réutilisable)

Ce projet isole standardise la documentation de n'importe quel projet:

- édition LaTeX dans VS Code;
- compilation PDF en direct;
- environnement isolé via Docker/Dev Container;
- captures de code propres;
- captures réelles de fenêtre VS Code;
- templates rapport/mémoire réutilisables.

Chemin du projet isolé:
`/home/pmt/KeurYaAicha/nv/keur_ya_aicha/Documentaion_des_projet`

## 1. Résultat final attendu

Tu dois pouvoir:

1. ouvrir ce projet dans un conteneur;
2. choisir un template (`report` ou `memoire`);
3. modifier `docs/main.tex`;
4. sauvegarder et voir le PDF se mettre à jour;
5. générer des captures code (stylisées et réelles);
6. exporter `docs/build/main.pdf`.

## 2. Architecture du projet isolé

```text
Documentaion_des_projet/
  .devcontainer/
    Dockerfile
    devcontainer.json
  .vscode/
    settings.json
    tasks.json
    extensions.json
  docs/
    main.tex
    captures/
  scripts/
    build.sh
    watch.sh
    clean.sh
    capture-code-silicon.sh
    capture-vscode-window.py
    init-template.sh
    doctor.sh
  templates/
    report/main.tex
    memoire/main.tex
  package.json
```

## 3. Prérequis machine hôte

- VS Code
- Docker Engine + Docker Compose
- Extension VS Code: `Dev Containers`
- Pour capture réelle VS Code (Linux):
  - `wmctrl`, `xdotool`, `xwininfo`
  - `python3-pil`

Installation Linux:

```bash
sudo apt update
sudo apt install -y wmctrl xdotool x11-utils python3-pil
```

## 4. Extensions VS Code

- `James-Yu.latex-workshop`
- `ms-vscode-remote.remote-containers`
- `adpyke.codesnap` (optionnel)

## 5. Démarrage rapide

Depuis `Documentaion_des_projet`:

1. Ouvrir le dossier dans VS Code.
2. `Ctrl+Shift+P` -> `Dev Containers: Reopen in Container`.
3. Choisir un template:

```bash
npm run doc:init:report
# ou
npm run doc:init:memoire
```

4. Compiler:

```bash
npm run doc:build
```

5. Compilation continue:

```bash
npm run doc:watch
```

## 6. Packagiste (npm) et objectif

`package.json` sert de point d'entrée unique pour documenter n'importe quel projet:

- `npm run doctor`: vérification environnement
- `npm run doc:init:report`: init template report via Docker
- `npm run doc:init:memoire`: init template memoire via Docker
- `npm run doc:build`: build PDF via Docker
- `npm run doc:watch`: watch PDF via Docker
- `npm run doc:clean`: clean via Docker
- `npm run build`: build PDF
- `npm run watch`: build continu
- `npm run clean`: nettoyage
- `npm run template:list`: liste templates
- `npm run template:init:report`
- `npm run template:init:memoire`
- `npm run capture:code -- <fichier> <debut> <fin> <sortie>`
- `npm run capture:vscode -- --source <fichier> --line <n> --output <png>`

## 7. Captures de code

### 7.1 Capture stylisée (`silicon`)

```bash
npm run capture:code -- /chemin/projet/src/app.ts 10 80 docs/captures/app-ts.png
```

### 7.2 Capture réelle de fenêtre VS Code

```bash
npm run capture:vscode -- \
  --source /chemin/projet/src/app.ts \
  --line 120 \
  --output docs/captures/reelle-vscode.png
```

## 8. Insertion dans LaTeX

Dans `docs/main.tex`:

```tex
\usepackage{graphicx}

\begin{figure}[h]
  \centering
  \includegraphics[width=\linewidth]{captures/reelle-vscode.png}
  \caption{Capture de code depuis VS Code}
\end{figure}
```

## 9. Documenter un projet externe (n'importe quelle stack)

Principe: ce projet reste isolé, mais il capture des fichiers d'un autre projet via chemins absolus.

Exemple:

```bash
npm run capture:vscode -- \
  --source /home/pmt/KeurYaAicha/nv/keur_ya_aicha/frontend/src/main.tsx \
  --line 45 \
  --output docs/captures/frontend-main.png
```

Tu gardes la documentation et le PDF dans `Documentaion_des_projet`, sans polluer le projet source.

## 10. Dépannage rapide

### `latexmk: command not found`
Utiliser les scripts Docker (`npm run doc:build`) au lieu du mode local.

### PDF ne bouge pas
- vérifier `latex-workshop.latex.autoBuild.run = onSave`
- relancer `npm run build`

### Capture VS Code réelle échoue
- vérifier `echo $DISPLAY`
- lancer `npm run doctor`
- vérifier `wmctrl`, `xdotool`, `xwininfo`, `python3-pil`

### Image non trouvée dans LaTeX
- vérifier chemin relatif depuis `docs/main.tex`
- éviter espaces/accents dans le nom de fichier image

## 11. Fichiers principaux

- Guide complet: `DOCUMENTATION_COMPLETE_LATEX_DOCKER_VSCODE.md`
- Entrée principale: `README.md`
- Configuration packagiste: `package.json`
- Template rapport: `templates/report/main.tex`
- Template mémoire: `templates/memoire/main.tex`
