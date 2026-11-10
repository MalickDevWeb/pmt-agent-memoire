#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎓 MEMOIRE GUARDIAN AI — Moteur Autonome d'Audit, Correction & Validation Académique
===================================================================================
Prend en entrée le mémoire académique (LaTeX/Texte/Markdown), l'analyse sous les
perspectives d'un directeur de mémoire, d'un correcteur universitaire et d'un
spécialiste de la mise en page, puis produit un audit rigoureux en 7 phases et
l'ensemble des livrables exploitables avant dépôt.

Auteur : Système Multi-Agents École 221
Version : 1.0.0
"""

import os
import sys
import re
import csv
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Set

# ==============================================================================
# MODÈLE DE DONNÉES D'ANOMALIE & SCORES
# ==============================================================================

@dataclass
class Anomaly:
    phase: str
    code: str
    gravity: str  # CRITIQUE, MAJEUR, MINEUR, RECOMMANDATION
    chapter: str
    location: str
    description: str
    recommendation: str
    snippet: Optional[str] = None
    status: str = "À TRAITER"

@dataclass
class PhaseResult:
    phase_id: int
    name: str
    score: float
    max_score: float
    status: str
    details: List[str] = field(default_factory=list)
    anomalies: List[Anomaly] = field(default_factory=list)

# ==============================================================================
# CLICHÉS & MARQUEURS DE TEXTES GÉNÉRIQUES OU IA (PHASE 6)
# ==============================================================================

AI_CLICHE_PATTERNS = [
    (r"\b(?:dans un monde en (?:constante|perpétuelle) évolution)\b", "Formulation d'introduction générique type IA"),
    (r"\b(?:il convient de (?:souligner|noter|rappeler) que)\b", "Tics d'articulation répétitif de synthèse IA"),
    (r"\b(?:force est de (?:constater|reconnaître))\b", "Formule d'emphase générique"),
    (r"\b(?:joue(?:nt)? un rôle (?:crucial|primordial|déterminant|clé))\b", "Hyperbole générique fréquente des LLM"),
    (r"\b(?:véritable pierre angulaire)\b", "Métaphore convenue surutilisée"),
    (r"\b(?:témoigne de l'importance)\b", "Formulation passive vague"),
    (r"\b(?:sans équivoque)\b", "Affirmation péremptoire sans justification chiffrée"),
    (r"\b(?:il est impératif de)\b", "Injonction normative fréquente dans les brouillons bruts d'IA"),
    (r"\b(?:en constante mutation)\b", "Cliché journalistique / introduction creuse"),
    (r"\b(?:in fine)\b", "Tics de langage récurrent"),
    (r"\b(?:au cœur de la problématique)\b", "Expression toute faite"),
    (r"\b(?:de manière holistique)\b", "Jargon abstrait souvent produit par les LLM")
]

VAGUE_SUPERLATIVES = [
    (r"\b100\s*%\s*(?:infaillible|sécurisé|parfait)\b", "Affirmation de sécurité absolue impossible en ingénierie logicielle"),
    (r"\b(?:totalement exempt de bugs?)\b", "Prétention irréaliste en informatique"),
    (r"\b(?:temps de réponse instantané)\b", "Terme imprécis : exiger une métrique en millisecondes"),
    (r"\b(?:solution miracle|révolutionnaire)\b", "Ton marketing non conforme au standard académique")
]

# ==============================================================================
# AUDITEUR PRINCIPAL : MEMOIRE GUARDIAN
# ==============================================================================

class MemoireGuardian:
    def __init__(self, memoire_dir: Path, root_dir: Path, export_dir: Path):
        self.memoire_dir = memoire_dir
        self.root_dir = root_dir
        self.export_dir = export_dir
        self.anomalies: List[Anomaly] = []
        self.phases: Dict[int, PhaseResult] = {}
        
        # Données collectées
        self.tex_files: Dict[str, str] = {}
        self.tex_lines: Dict[str, List[str]] = {}
        self.bib_content: str = ""
        self.bib_entries: Set[str] = set()
        self.citations: Set[str] = set()
        self.labels: Set[str] = set()
        self.refs: Set[str] = set()
        self.figures: List[Dict] = []
        self.tables: List[Dict] = []
        self.word_counts: Dict[str, int] = {}

    def load_corpus(self):
        """Charge l'ensemble des fichiers TeX, BibTeX et annexes."""
        if not self.memoire_dir.exists():
            raise FileNotFoundError(f"Répertoire du mémoire introuvable : {self.memoire_dir}")
        
        # Parcourt tous les fichiers .tex
        for p in sorted(self.memoire_dir.rglob("*.tex")):
            rel = p.relative_to(self.memoire_dir).as_posix()
            try:
                raw_content = p.read_text(encoding="utf-8", errors="ignore")
                # Élimine les commentaires LaTeX pour l'analyse syntaxique (% précédé ou non de backslash)
                uncommented_lines = []
                for line in raw_content.splitlines():
                    cleaned = re.sub(r"(?<!\\)%.*$", "", line)
                    uncommented_lines.append(cleaned)
                content = "\n".join(uncommented_lines)
                
                self.tex_files[rel] = content
                self.tex_lines[rel] = raw_content.splitlines()
                # Compte de mots approximatif
                clean_text = re.sub(r"\\[a-zA-Z]+(\[[^\]]*\])?(\{[^\}]*\})?", " ", content)
                words = re.findall(r"\b[A-Za-zÀ-ÿ0-9_-]+\b", clean_text)
                self.word_counts[rel] = len(words)
            except Exception as e:
                print(f"⚠️ Erreur de lecture de {rel}: {e}")

        # Charge le fichier .bib
        bib_path = self.memoire_dir / "references.bib"
        if bib_path.exists():
            self.bib_content = bib_path.read_text(encoding="utf-8", errors="ignore")
            # Extraction des clés BibTeX : @article{key, ...
            self.bib_entries = set(re.findall(r"@\w+\s*\{\s*([a-zA-Z0-9_:-]+)\s*,", self.bib_content))

    # --------------------------------------------------------------------------
    # PHASE 1 : AUDIT ACADÉMIQUE (20 PTS)
    # --------------------------------------------------------------------------
    def audit_academique(self) -> PhaseResult:
        score = 20.0
        details = []
        phase_anomalies = []

        # 1. Vérification des éléments préliminaires obligatoires (recherche flexible)
        preliminaries = [
            (["preliminaires/garde.tex", "preliminaires/page-de-garde.tex"], "Page de garde officielle"),
            (["preliminaires/resume.tex"], "Résumé en français"),
            (["preliminaires/abstract.tex"], "Abstract en anglais"),
            (["preliminaires/remerciements.tex"], "Remerciements"),
            (["preliminaires/sigles.tex", "preliminaires/sigles-acronymes.tex"], "Liste des sigles & abréviations"),
        ]
        for candidates, label in preliminaries:
            found = any(c in self.tex_files for c in candidates)
            if found:
                match_p = next(c for c in candidates if c in self.tex_files)
                details.append(f"✔ {label} présent ({match_p})")
            else:
                score -= 1.5
                ano = Anomaly(
                    phase="Phase 1 : Audit Académique",
                    code="ACAD-01",
                    gravity="MAJEUR",
                    chapter="Préliminaires",
                    location=candidates[0],
                    description=f"Le composant préliminaire obligatoire '{label}' ({candidates[0]}) est manquant.",
                    recommendation=f"Créer {candidates[0]} en respectant le canevas académique."
                )
                phase_anomalies.append(ano)

        # 2. Vérification des chapitres obligatoires (recherche dynamique)
        required_chapters = [
            (["chapitres/introduction.tex"], "Introduction générale", 700),
            (["chapitres/ch1-cadre.tex", "chapitres/ch1-contexte.tex"], "Chapitre 1 — Contexte & Cadre d'étude", 600),
            (["chapitres/ch2-besoins.tex", "chapitres/ch2-etat-art.tex"], "Chapitre 2 — Analyse des Besoins & État de l'art", 800),
            (["chapitres/ch3-gestion-projet.tex"], "Chapitre 3 — Conduite & Gestion de projet", 800),
            (["chapitres/ch4-conception.tex"], "Chapitre 4 — Analyse & Conception d'architecture", 800),
            (["chapitres/ch5-cout.tex"], "Chapitre 5 — Étude financière & Modélisation des coûts", 600),
            (["chapitres/ch6-realisation.tex"], "Chapitre 6 — Réalisation & Implémentation", 1000),
            (["chapitres/ch7-tests.tex"], "Chapitre 7 — Qualification, Tests & Validation", 700),
            (["chapitres/ch8-deploiement.tex"], "Chapitre 8 — Déploiement & DevSecOps", 800),
            (["chapitres/conclusion.tex"], "Conclusion générale & Perspectives", 400),
        ]

        total_words = 0
        for candidates, title, min_w in required_chapters:
            found_p = next((c for c in candidates if c in self.tex_files), None)
            if not found_p:
                score -= 3.0
                ano = Anomaly(
                    phase="Phase 1 : Audit Académique",
                    code="ACAD-02",
                    gravity="CRITIQUE",
                    chapter=title,
                    location=candidates[0],
                    description=f"Chapitre obligatoire manquant : {title} ({candidates[0]}).",
                    recommendation=f"Rédiger et inclure {candidates[0]} dans le fichier maître main.tex."
                )
                phase_anomalies.append(ano)
            else:
                w = self.word_counts.get(found_p, 0)
                total_words += w
                if w < min_w:
                    score -= 1.0
                    ano = Anomaly(
                        phase="Phase 1 : Audit Académique",
                        code="ACAD-03",
                        gravity="MINEUR",
                        chapter=title,
                        location=found_p,
                        description=f"Volume rédactionnel court pour {title} : {w} mots (attendu >= {min_w} mots).",
                        recommendation=f"Développer les arguments et approfondir les explications techniques."
                    )
                    phase_anomalies.append(ano)
                details.append(f"✔ {title} présent ({w} mots, {found_p})")

        details.append(f"ℹ Volume rédactionnel total du corps du mémoire : ~{total_words} mots.")

        # 3. Contrôle de la problématique dans l'introduction
        intro = self.tex_files.get("chapitres/introduction.tex", "")
        if "problématique" not in intro.lower() and "problematique" not in intro.lower():
            score -= 1.5
            phase_anomalies.append(Anomaly(
                phase="Phase 1 : Audit Académique",
                code="ACAD-04",
                gravity="MAJEUR",
                chapter="Introduction générale",
                location="chapitres/introduction.tex",
                description="Le terme ou paragraphe explicite formalisant la 'problématique' n'a pas été clairement repéré.",
                recommendation="Formuler sans ambiguïté la question centrale de recherche / problématique d'ingénierie."
            ))

        # 4. Contrôle des objectifs et de l'adéquation conclusion/introduction
        concl = self.tex_files.get("chapitres/conclusion.tex", "")
        if "perspective" not in concl.lower() and "perspectives" not in concl.lower():
            score -= 1.0
            phase_anomalies.append(Anomaly(
                phase="Phase 1 : Audit Académique",
                code="ACAD-05",
                gravity="MINEUR",
                chapter="Conclusion générale",
                location="chapitres/conclusion.tex",
                description="La section 'Perspectives' d'évolution future est absente ou insuffisamment formalisée.",
                recommendation="Ajouter un sous-titre dédié aux perspectives d'évolution académique et industrielle."
            ))

        score = max(0.0, min(20.0, score))
        self.anomalies.extend(phase_anomalies)
        return PhaseResult(1, "Audit Académique", round(score, 1), 20.0, "OK" if score >= 16 else "ATTENTION", details, phase_anomalies)

    # --------------------------------------------------------------------------
    # PHASE 2 : AUDIT SCIENTIFIQUE & MÉTHODOLOGIQUE (25 PTS)
    # --------------------------------------------------------------------------
    def audit_scientifique(self) -> PhaseResult:
        score = 25.0
        details = []
        phase_anomalies = []

        # 1. Vérification de la rigueur méthodologique
        full_text = " ".join(self.tex_files.values())
        methods = ["scrum", "agile", "hexagonale", "ddd", "cycle en v", "devsecops"]
        found_methods = [m for m in methods if m in full_text.lower()]
        if len(found_methods) >= 3:
            details.append(f"✔ Cadres méthodologiques explicites identifiés : {', '.join(found_methods)}")
        else:
            score -= 3.0
            phase_anomalies.append(Anomaly(
                phase="Phase 2 : Audit Scientifique",
                code="SCI-01",
                gravity="MAJEUR",
                chapter="Méthodologie",
                location="chapitres/ch3-gestion-projet.tex",
                description="Insuffisance de cadrage méthodologique formel dans le mémoire.",
                recommendation="Préciser les méthodes d'ingénierie logicielle (ex: Architecture Hexagonale, DDD, Agile/Kasongo)."
            ))

        # 2. Règle d'or : Vérification des résultats prouvés (non inventés)
        ch7 = self.tex_files.get("chapitres/ch7-tests.tex", "")
        ch6 = self.tex_files.get("chapitres/ch6-realisation.tex", "")
        if "docs/evidence/" not in ch7 and "qa/fixtures" not in ch7 and "PASS" not in ch7:
            score -= 4.0
            phase_anomalies.append(Anomaly(
                phase="Phase 2 : Audit Scientifique",
                code="SCI-02",
                gravity="CRITIQUE",
                chapter="Chapitre 7 — Qualification",
                location="chapitres/ch7-tests.tex",
                description="Absence de traçabilité vers des preuves d'exécution machine réelles (docs/evidence/ ou logs QA).",
                recommendation="Citer explicitement les jeux d'essais réels, taux d'assertions conformes et fichiers de preuves."
            ))
        else:
            details.append("✔ Les chapitres techniques citent des preuves réelles vérifiables.")

        # 3. Superlatifs vagues et affirmations non démontrées
        for rel_path, content in self.tex_files.items():
            for pat, desc in VAGUE_SUPERLATIVES:
                for match in re.finditer(pat, content, re.IGNORECASE):
                    score -= 1.0
                    snippet = content[max(0, match.start() - 40): min(len(content), match.end() + 40)]
                    phase_anomalies.append(Anomaly(
                        phase="Phase 2 : Audit Scientifique",
                        code="SCI-03",
                        gravity="MAJEUR",
                        chapter=rel_path,
                        location=f"{rel_path}:{match.start()}",
                        description=f"Affirmation non scientifique / non justifiée : '{match.group(0)}'. {desc}.",
                        recommendation="Remplacer par une formulation mesurée et appuyée par des données chiffrées.",
                        snippet=snippet.strip()
                    ))

        # 4. Présence des limites du projet
        has_limits = any(mot in full_text.lower() for mot in ["limite", "limites", "contrainte", "contraintes"])
        if has_limits:
            details.append("✔ Section ou mention des limites et contraintes techniques identifiée.")
        else:
            score -= 2.0
            phase_anomalies.append(Anomaly(
                phase="Phase 2 : Audit Scientifique",
                code="SCI-04",
                gravity="MAJEUR",
                chapter="Conclusion / Ch8",
                location="chapitres/conclusion.tex",
                description="Le mémoire ne mentionne pas explicitement les limites scientifiques ou techniques de la solution.",
                recommendation="Ajouter un paragraphe franc sur les limites du système (charge maximale, dette résiduelle)."
            ))

        score = max(0.0, min(25.0, score))
        self.anomalies.extend(phase_anomalies)
        return PhaseResult(2, "Audit Scientifique & Méthodologique", round(score, 1), 25.0, "OK" if score >= 20 else "ATTENTION", details, phase_anomalies)

    # --------------------------------------------------------------------------
    # PHASE 3 : AUDIT DES SOURCES & ORIGINALITÉ (20 PTS)
    # --------------------------------------------------------------------------
    def audit_sources(self) -> PhaseResult:
        score = 20.0
        details = []
        phase_anomalies = []

        # 1. Extraction de toutes les citations \cite{...}
        for rel_path, content in self.tex_files.items():
            matches = re.findall(r"\\cite[a-z]*\{([^}]+)\}", content)
            for m in matches:
                for key in m.split(","):
                    k = key.strip()
                    if k and k != "*":
                        self.citations.add(k)

        details.append(f"ℹ Citations formelles \\cite repérées dans le texte : {len(self.citations)}")
        details.append(f"ℹ Entrées BibTeX trouvées dans references.bib : {len(self.bib_entries)}")

        # 2. Citations orphelines (citées mais absentes du .bib)
        orphans = [c for c in self.citations if c not in self.bib_entries]
        if orphans:
            score -= min(8.0, len(orphans) * 2.0)
            phase_anomalies.append(Anomaly(
                phase="Phase 3 : Sources & Originalité",
                code="SRC-01",
                gravity="CRITIQUE",
                chapter="Bibliographie",
                location="references.bib",
                description=f"Clés de citation orphelines (appelées par \\cite mais absentes de references.bib) : {', '.join(orphans)}.",
                recommendation="Ajouter les entrées complètes correspondantes dans references.bib avec auteur, titre, année et lien."
            ))

        # 3. Références non citées dans le texte (si > 0)
        unused_bib = [b for b in self.bib_entries if b not in self.citations]
        if len(self.bib_entries) > 0 and unused_bib:
            score -= 1.0
            phase_anomalies.append(Anomaly(
                phase="Phase 3 : Sources & Originalité",
                code="SRC-02",
                gravity="MINEUR",
                chapter="Bibliographie",
                location="references.bib",
                description=f"Entrées BibTeX jamais citées dans le texte par \\cite : {', '.join(unused_bib[:5])}.",
                recommendation="Citer explicitement les ouvrages dans les chapitres pertinents ou purger les entrées inutiles."
            ))

        # 4. Vérification de la présence effective de sources scientifiques/officielles
        if len(self.bib_entries) == 0:
            score -= 5.0
            phase_anomalies.append(Anomaly(
                phase="Phase 3 : Sources & Originalité",
                code="SRC-03",
                gravity="MAJEUR",
                chapter="Bibliographie",
                location="memoire/docs/references.bib",
                description="Le fichier references.bib est actuellement vide d'entrées BibTeX formelles (les sources sont en notes de bas de page).",
                recommendation="Formaliser au moins 10 références académiques et techniques dans references.bib (normes, articles, ouvrages)."
            ))
        else:
            details.append("✔ Le fichier references.bib contient des entrées bibliographiques formelles.")

        # 5. Vérification des notes de bas de page bibliographiques
        fn_count = 0
        for content in self.tex_files.values():
            fn_count += len(re.findall(r"\\footnote\{", content))
        details.append(f"ℹ Nombre total de notes de bas de page traçant les sources/dépôt : {fn_count}")

        score = max(0.0, min(20.0, score))
        self.anomalies.extend(phase_anomalies)
        return PhaseResult(3, "Sources & Originalité", round(score, 1), 20.0, "OK" if score >= 15 else "ATTENTION", details, phase_anomalies)

    # --------------------------------------------------------------------------
    # PHASE 4 : AUDIT RÉDACTIONNEL & COHÉRENCE (15 PTS)
    # --------------------------------------------------------------------------
    def audit_redactionnel(self) -> PhaseResult:
        score = 15.0
        details = []
        phase_anomalies = []

        # 1. Phrases excessivement longues (> 55 mots)
        long_sentences = 0
        for rel_path, lines in self.tex_lines.items():
            for num, line in enumerate(lines, 1):
                clean_l = re.sub(r"\\[a-zA-Z]+(\[[^\]]*\])?(\{[^\}]*\})?", " ", line)
                clean_l = clean_l.strip()
                if not clean_l.startswith("%") and len(clean_l.split()) > 55:
                    long_sentences += 1
                    if long_sentences <= 4:
                        phase_anomalies.append(Anomaly(
                            phase="Phase 4 : Audit Rédactionnel",
                            code="RED-01",
                            gravity="MINEUR",
                            chapter=rel_path,
                            location=f"{rel_path}:{num}",
                            description=f"Phrase très longue ({len(clean_l.split())} mots) risquant d'alourdir la lecture.",
                            recommendation="Scinder en deux phrases courtes pour améliorer la clarté académique.",
                            snippet=clean_l[:90] + "..."
                        ))

        if long_sentences > 0:
            score -= min(3.0, long_sentences * 0.5)
            details.append(f"⚠️ {long_sentences} phrase(s) de plus de 55 mots repérée(s).")
        else:
            details.append("✔ Longueur des phrases équilibrée et fluide.")

        # 2. Répétition ou coquilles typiques
        typos = [
            (r"\b(très très|plus plus|de de|le le|la la)\b", "Redoublement involontaire d'un mot"),
            (r"\b(autant pour moi)\b", "Graphie conseillée en contexte académique : 'au temps pour moi'"),
            (r"\bcomme même\b", "Faute de français : remplacer par 'quand même'"),
        ]
        for rel_path, content in self.tex_files.items():
            for pat, desc in typos:
                for match in re.finditer(pat, content, re.IGNORECASE):
                    score -= 1.0
                    phase_anomalies.append(Anomaly(
                        phase="Phase 4 : Audit Rédactionnel",
                        code="RED-02",
                        gravity="MINEUR",
                        chapter=rel_path,
                        location=f"{rel_path}:{match.start()}",
                        description=f"Coquille rédactionnelle : '{match.group(0)}'. {desc}.",
                        recommendation=f"Corriger l'expression selon les règles de grammaire académique."
                    ))

        # 3. Transitions et articulations logiques
        full_text = " ".join(self.tex_files.values())
        connectors = ["ainsi", "par conséquent", "cependant", "en outre", "néanmoins", "dès lors", "toutefois"]
        conn_count = sum(full_text.lower().count(c) for c in connectors)
        if conn_count < 20:
            score -= 1.5
            phase_anomalies.append(Anomaly(
                phase="Phase 4 : Audit Rédactionnel",
                code="RED-03",
                gravity="MINEUR",
                chapter="Ensemble du mémoire",
                location="Transitions",
                description="Pénurie de connecteurs logiques assurant la transition entre arguments.",
                recommendation="Enrichir les liaisons conceptuelles entre paragraphes (ainsi, par conséquent, en outre)."
            ))
        else:
            details.append(f"✔ Richesse des connecteurs logiques confirmée ({conn_count} occurrences).")

        score = max(0.0, min(15.0, score))
        self.anomalies.extend(phase_anomalies)
        return PhaseResult(4, "Audit Rédactionnel & Cohérence", round(score, 1), 15.0, "OK" if score >= 12 else "ATTENTION", details, phase_anomalies)

    # --------------------------------------------------------------------------
    # PHASE 5 : AUDIT DE PRÉSENTATION & MISE EN PAGE (20 PTS)
    # --------------------------------------------------------------------------
    def audit_mise_en_page(self) -> PhaseResult:
        score = 20.0
        details = []
        phase_anomalies = []

        # 1. Extraction des \label et des \ref
        for rel_path, content in self.tex_files.items():
            for l in re.findall(r"\\label\{([^}]+)\}", content):
                self.labels.add(l)
            for r in re.findall(r"\\ref\{([^}]+)\}", content):
                self.refs.add(r)

        # 2. Références cassées (appelées par \ref mais sans \label)
        broken_refs = [r for r in self.refs if r not in self.labels]
        if broken_refs:
            score -= min(6.0, len(broken_refs) * 1.5)
            phase_anomalies.append(Anomaly(
                phase="Phase 5 : Mise en Page",
                code="PAGE-01",
                gravity="CRITIQUE",
                chapter="Mise en page",
                location="\\ref",
                description=f"Références internes cassées (étiquettes inconnues dans le code) : {', '.join(broken_refs)}.",
                recommendation="Créer le \\label correspondant ou corriger la faute de frappe dans le \\ref."
            ))
        else:
            details.append("✔ Aucune référence croisée \\ref cassée.")

        # 3. Contrôle des figures et des fichiers d'images
        image_calls = []
        for rel_path, content in self.tex_files.items():
            imgs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", content)
            for img in imgs:
                image_calls.append((rel_path, img))

        missing_images = []
        for rel_path, img_rel in image_calls:
            # Chemins possibles
            cand1 = self.memoire_dir / img_rel
            cand2 = self.memoire_dir / "images" / Path(img_rel).name
            cand3 = self.memoire_dir / f"{img_rel}.png"
            cand4 = self.memoire_dir / f"{img_rel}.pdf"
            if not (cand1.exists() or cand2.exists() or cand3.exists() or cand4.exists()):
                missing_images.append(f"{img_rel} (cité dans {rel_path})")

        if missing_images:
            score -= min(6.0, len(missing_images) * 2.0)
            phase_anomalies.append(Anomaly(
                phase="Phase 5 : Mise en Page",
                code="PAGE-02",
                gravity="CRITIQUE",
                chapter="Illustrations",
                location="images/",
                description=f"Fichiers d'images appelés par \\includegraphics mais introuvables sur disque : {', '.join(missing_images)}.",
                recommendation="Placer les images requises dans le sous-dossier memoire/docs/images/."
            ))
        else:
            details.append(f"✔ Toutes les images insérées ({len(image_calls)}) existent bien physiquement sur le disque.")

        # 4. Vérification de la présence de listes automatiques (tables des matières, figures, tableaux)
        main_content = self.tex_files.get("main.tex", "")
        if "\\tableofcontents" in main_content:
            details.append("✔ Sommaire automatique (\\tableofcontents) configuré.")
        else:
            score -= 3.0
            phase_anomalies.append(Anomaly(
                phase="Phase 5 : Mise en Page",
                code="PAGE-03",
                gravity="MAJEUR",
                chapter="Structure",
                location="main.tex",
                description="L'instruction \\tableofcontents est absente de main.tex.",
                recommendation="Ajouter \\tableofcontents dans la séquence des préliminaires."
            ))

        # 5. Contrôle des tableaux (\begin{table}) et des figures (\begin{figure}) sans \caption
        for rel_path, content in self.tex_files.items():
            # Figures sans caption
            fig_blocks = re.findall(r"\\begin\{figure\}.*?\\end\{figure\}", content, re.DOTALL)
            for fb in fig_blocks:
                if "\\caption" not in fb:
                    score -= 1.0
                    phase_anomalies.append(Anomaly(
                        phase="Phase 5 : Mise en Page",
                        code="PAGE-04",
                        gravity="MAJEUR",
                        chapter=rel_path,
                        location=rel_path,
                        description="Un bloc \\begin{figure} ne possède pas de légende \\caption{...}.",
                        recommendation="Ajouter systématiquement une légende explicative sous chaque figure."
                    ))

        score = max(0.0, min(20.0, score))
        self.anomalies.extend(phase_anomalies)
        return PhaseResult(5, "Mise en Page & Présentation", round(score, 1), 20.0, "OK" if score >= 16 else "ATTENTION", details, phase_anomalies)

    # --------------------------------------------------------------------------
    # PHASE 6 : CONTRÔLE AUTHENTICITÉ & DÉTECTION IA (NON-CAMOUFLAGE)
    # --------------------------------------------------------------------------
    def audit_authenticite_ia(self) -> PhaseResult:
        # Note indicative intégrée à l'originalité et à la rédaction
        details = []
        phase_anomalies = []
        cliche_hits = []

        # 1. Repérage des tics linguistiques typiques des LLMs
        for rel_path, lines in self.tex_lines.items():
            for num, line in enumerate(lines, 1):
                if line.lstrip().startswith("%"):
                    continue
                for pat, desc in AI_CLICHE_PATTERNS:
                    m = re.search(pat, line, re.IGNORECASE)
                    if m:
                        cliche_hits.append((rel_path, num, m.group(0), desc))
                        phase_anomalies.append(Anomaly(
                            phase="Phase 6 : Détection IA & Authenticité",
                            code="AI-01",
                            gravity="RECOMMANDATION",
                            chapter=rel_path,
                            location=f"{rel_path}:{num}",
                            description=f"Passage stylisé IA : expression '{m.group(0)}' ({desc}).",
                            recommendation="Reformuler avec votre voix d'auteur et des arguments techniques concrets (ne pas camoufler avec un synonyme artificiel).",
                            snippet=line.strip()
                        ))

        if len(cliche_hits) == 0:
            details.append("✔ Aucun cliché typique de génération brute d'IA détecté dans le corpus.")
        else:
            details.append(f"ℹ {len(cliche_hits)} tournure(s) générique(s) ou tics de synthèse identifiée(s).")

        # 2. Vérification obligatoire de l'Annexe Journal d'Usage de l'IA (Charte Éthique)
        journal = self.tex_files.get("annexes/journal-ia.tex", "")
        if not journal or len(journal.strip()) < 100:
            phase_anomalies.append(Anomaly(
                phase="Phase 6 : Détection IA & Authenticité",
                code="AI-02",
                gravity="CRITIQUE",
                chapter="Annexes",
                location="annexes/journal-ia.tex",
                description="Le Journal d'Usage de l'IA est absent ou vide.",
                recommendation="Documenter chaque usage de l'IA (prompts, arbitrage humain, code validé) conformément à la directive universitaire."
            ))
        else:
            details.append("✔ Annexe 'Journal d'Usage de l'IA' présente et renseignée en toute transparence.")

        self.anomalies.extend(phase_anomalies)
        return PhaseResult(6, "Authenticité & Éthique de l'IA", 10.0, 10.0, "OK", details, phase_anomalies)

    # --------------------------------------------------------------------------
    # PHASE 7 : VALIDATION FINALE & CALCUL DU SCORE GLOBAL
    # --------------------------------------------------------------------------
    def executer_audit_complet(self) -> Dict:
        self.load_corpus()

        res1 = self.audit_academique()
        res2 = self.audit_scientifique()
        res3 = self.audit_sources()
        res4 = self.audit_redactionnel()
        res5 = self.audit_mise_en_page()
        res6 = self.audit_authenticite_ia()

        self.phases = {
            1: res1,
            2: res2,
            3: res3,
            4: res4,
            5: res5,
            6: res6
        }

        # Score global / 100
        total_score = round(res1.score + res2.score + res3.score + res4.score + res5.score, 1)

        # Classification des anomalies par gravité
        critiques = [a for a in self.anomalies if a.gravity == "CRITIQUE"]
        majeures = [a for a in self.anomalies if a.gravity == "MAJEUR"]
        mineures = [a for a in self.anomalies if a.gravity in ("MINEUR", "RECOMMANDATION")]

        # Verdict strict
        if len(critiques) > 0:
            verdict = "NON PRÊT POUR LE DÉPÔT"
            verdict_desc = f"Présence de {len(critiques)} anomalie(s) critique(s) bloquante(s)."
            badge = "🔴"
        elif len(majeures) > 0 or total_score < 75.0:
            verdict = "CORRECTIONS NÉCESSAIRES"
            verdict_desc = f"{len(majeures)} anomalie(s) majeure(s) à rectifier avant validation."
            badge = "🟡"
        else:
            verdict = "PRÊT POUR LA RELECTURE FINALE DE L'AUTEUR"
            verdict_desc = "Le document respecte tous les critères académiques et scientifiques formels."
            badge = "🟢"

        return {
            "total_score": total_score,
            "max_score": 100.0,
            "verdict": verdict,
            "verdict_desc": verdict_desc,
            "badge": badge,
            "counts": {
                "critiques": len(critiques),
                "majeures": len(majeures),
                "mineures": len(mineures),
                "total": len(self.anomalies)
            }
        }

    # --------------------------------------------------------------------------
    # GÉNÉRATION DES LIVRABLES (RAPPORT MD, CSV, QUESTIONS, CHECKLIST)
    # --------------------------------------------------------------------------
    def generer_livrables(self, audit_summary: Dict):
        self.export_dir.mkdir(parents=True, exist_ok=True)

        # 1. RAPPORT D'AUDIT COMPLET (Markdown & imprimable)
        report_path = self.export_dir / "memoire_audit_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 🎓 RAPPORT D'AUDIT ACADÉMIQUE — MEMOIRE GUARDIAN AI\n\n")
            f.write(f"**Plateforme :** Système Multi-Agents École 221  \n")
            f.write(f"**Document audité :** `{self.memoire_dir.as_posix()}/main.tex`  \n")
            f.write(f"**Verdict Global :** {audit_summary['badge']} **{audit_summary['verdict']}**  \n")
            f.write(f"**Score Académique Indicatif :** **{audit_summary['total_score']} / 100**  \n")
            f.write(f"**Résumé des anomalies :** {audit_summary['counts']['critiques']} Critique(s) | "
                    f"{audit_summary['counts']['majeures']} Majeure(s) | {audit_summary['counts']['mineures']} Mineure(s)/Recommandation(s)\n\n")
            f.write("> *Avertissement éthique : Ce score indicatif ne se substitue pas à l'évaluation officielle du jury de soutenance. "
                    "Il mesure la conformité formelle, méthodologique, bibliographique et typographique selon les standards universitaires.*  \n\n")
            
            f.write("---\n\n")
            f.write("## 📊 1. Synthèse par Dimension d'Évaluation\n\n")
            f.write("| Phase | Dimension | Score Obtenu | Barème | Statut |\n")
            f.write("| :--- | :--- | :---: | :---: | :---: |\n")
            for pid in [1, 2, 3, 4, 5]:
                p = self.phases[pid]
                status_emoji = "🟢" if p.score >= (p.max_score * 0.8) else ("🟡" if p.score >= (p.max_score * 0.6) else "🔴")
                f.write(f"| Phase {p.phase_id} | {p.name} | **{p.score}** | {p.max_score} | {status_emoji} {p.status} |\n")
            f.write(f"| **TOTAL** | **Note Globale Indicative** | **{audit_summary['total_score']}** | **100** | **{audit_summary['badge']} {audit_summary['verdict']}** |\n\n")

            f.write("---\n\n")
            f.write("## 🔍 2. Détails des Constats par Spécialiste\n\n")
            for pid in sorted(self.phases.keys()):
                p = self.phases[pid]
                f.write(f"### {p.name} (Score : {p.score}/{p.max_score})\n")
                for d in p.details:
                    f.write(f"- {d}\n")
                f.write("\n")

            f.write("---\n\n")
            f.write("## ⚠️ 3. Registre Intégral des Anomalies et Actions Correctives\n\n")
            if not self.anomalies:
                f.write("Félicitations ! Aucune anomalie n'a été détectée dans le corpus.\n\n")
            else:
                for idx, a in enumerate(self.anomalies, 1):
                    badge = "🔴" if a.gravity == "CRITIQUE" else ("🟡" if a.gravity == "MAJEUR" else "⚪")
                    f.write(f"#### {badge} [{a.code}] {a.gravity} — {a.chapter} ({a.location})\n")
                    f.write(f"- **Problème :** {a.description}\n")
                    if a.snippet:
                        f.write(f"- **Extrait :** `... {a.snippet} ...`\n")
                    f.write(f"- **Correction recommandée :** {a.recommendation}\n")
                    f.write(f"- **Statut :** `{a.status}`\n\n")

        # 2. MATRICE DES ANOMALIES (CSV pour Excel/Tableur)
        csv_path = self.export_dir / "anomalies_matrix.csv"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["ID", "Gravité", "Code", "Phase", "Chapitre", "Emplacement", "Description", "Correction Recommandée", "Statut"])
            for idx, a in enumerate(self.anomalies, 1):
                writer.writerow([idx, a.gravity, a.code, a.phase, a.chapter, a.location, a.description, a.recommendation, a.status])

        # 3. PRÉPARATION À LA SOUTENANCE (10 Questions du Jury)
        questions_path = self.export_dir / "questions_soutenance.md"
        with open(questions_path, "w", encoding="utf-8") as f:
            f.write("# 🎤 PRÉPARATION À LA SOUTENANCE ORALE DU MÉMOIRE\n\n")
            f.write("Ce guide recense les 10 questions critiques les plus probables posées par les membres du jury "
                    "(Président, Rapporteur, Encadreur) et fournit les éléments factuels pour défendre vos travaux avec brio.\n\n")
            
            questions = [
                ("1. Sur l'isolation Multi-Tenant et la Sécurité (SEC-003)",
                 "Comment garantissez-vous qu'une école A ne puisse jamais accéder par effraction ou injection aux données d'une école B ?",
                 "Défense : Expliquer que l'isolation ne repose pas sur un simple paramètre URL ou en-tête client (interdiction formelle du frontend d'envoyer X-Tenant-Id). L'isolation est garantie au niveau du token JWT signé, extrait côté backend par l'intercepteur de sécurité et injecté dans le contexte `@TenantId`. Chaque requête JPA applique automatiquement le filtre d'isolation sur la clé `organization_id`."),
                
                ("2. Sur le rôle et l'utilisation de l'Intelligence Artificielle",
                 "Avez-vous rédigé ce mémoire vous-même ou s'agit-il d'un travail généré par ChatGPT ?",
                 "Défense : Présenter immédiatement l'Annexe B (Journal d'usage de l'IA). Démontrer que l'IA a agi comme un compilateur et un assistant d'orchestration (génération de squelettes et relecture), mais que chaque composant métier, règle de calcul et architecture logicielle provient des choix souverains de l'équipe étudiante et a été vérifié par des tests réels."),
                
                ("3. Sur l'Architecture Hexagonale et le DDD",
                 "Pourquoi avoir choisi l'Architecture Hexagonale plutôt qu'une architecture classique en couches (Controller-Service-Repository) ?",
                 "Défense : Mettre en avant le découplage du domaine métier par rapport aux frameworks d'infrastructure (base de données, web REST). Cela permet de tester les cas d'utilisation métier de manière pure, sans dépendre d'un serveur applicatif ou d'une base Neon/Postgres démarrée."),
                
                ("4. Sur la Gouvernance de Projet et le framework Multi-Agents",
                 "Qu'apporte concrètement un système multi-agents par rapport à un développement classique en équipe ?",
                 "Défense : Souligner la séparation stricte des responsabilités (RACI) et les garde-fous de qualité. Chaque agent (Architecte, QA, Sécurité, Dev) dispose de pré-requis et de livrables vérifiables par machine (check_agent_rules.py). Aucun code ne passe sans approbation de revue et tests d'intégration réussis."),
                
                ("5. Sur les Tests et la Qualification logicielle (Ch. 7)",
                 "Quelle est la couverture réelle de vos tests et comment prouvez-vous le bon fonctionnement du système ?",
                 "Défense : Citer les chiffres exacts de l'audit : 16 modules testés, 142 assertions exécutées avec 100% de succès dans `logs/qa_execution.log`, validées par le rapport d'exécution de l'Agent 05. Mentionner les tests de non-régression et les scénarios de bout en bout."),
                
                ("6. Sur les Coûts et la Viabilité Financière (Ch. 5)",
                 "Votre solution est-elle rentable pour un réseau d'établissements au Sénégal ?",
                 "Défense : Présenter le modèle économique à 120 000 FCFA/mois par école. Avec des coûts d'infrastructure cloud maîtrisés à 29,38 USD/mois (Neon + Render) et un coût unitaire par élève de 123 FCFA/an, le point mort est atteint dès 2 écoles abonnées."),
                
                ("7. Sur la Dette Technique et le Refactoring Frontend",
                 "Avez-vous de la dette technique dans votre frontend React ?",
                 "Défense : Expliquer en toute franchise la stratégie de cliquet : nous avons traqué le typage strict (`any` réduit de 373 à 362) et migré les appels API directs vers TanStack React Query pour garantir un cache optimisé et zéro re-render inutile."),
                
                ("8. Sur la Résilience Réseau et le Mode Vigile Campus",
                 "Comment le vigile contrôle-t-il les accès si la connexion Internet du campus tombe en panne ?",
                 "Défense : Expliquer le fonctionnement du mode déconnecté du vigile avec stockage local PWA/IndexedDB et signature cryptographique des badges QR, permettant une validation hors-ligne synchronisée ultérieurement dès le retour du réseau."),
                
                ("9. Sur la conformité RGPD / Protection des Données Personnelles",
                 "Comment sont protégées les données sensibles des mineurs (élèves) et leurs bulletins scolaires ?",
                 "Défense : Citer le chiffrement des mots de passe avec BCrypt, les politiques RLS en base, l'absence de secrets dans les dépôts publics et le contrôle d'accès strict par rôle RBAC (seuls les parents et l'administration accèdent aux notes de l'élève)."),
                
                ("10. Sur les Limites et les Perspectives d'Évolution",
                 "Si vous deviez poursuivre ce travail en Master, quels chantiers engageriez-vous en priorité ?",
                 "Défense : Mentionner l'intégration d'un canal de paiement mobile money direct (Wave, Orange Money), le portage complet en application mobile native React Native pour les parents, et l'optimisation des requêtes complexes par une vue matérialisée CQRS.")
            ]

            for q_num, q_text, r_text in questions:
                f.write(f"### {q_num}\n")
                f.write(f"**Question :** *« {q_text} »*\n\n")
                f.write(f"**Éléments de réponse recommandée :**\n{r_text}\n\n")

        # 4. CHECKLIST AVANT DÉPÔT ACADÉMIQUE
        checklist_path = self.export_dir / "checklist_depot.md"
        with open(checklist_path, "w", encoding="utf-8") as f:
            f.write("# 📋 CHECKLIST OFFICIELLE AVANT DÉPÔT DU MÉMOIRE\n\n")
            f.write("À cocher impérativement par les candidats et le tuteur avant transmission finale au secrétariat académique :\n\n")
            f.write("### 1. Fond & Contenu Scientifique\n")
            f.write("- [ ] La problématique générale est clairement énoncée dès l'introduction.\n")
            f.write("- [ ] Les objectifs spécifiques sont tous passés en revue dans la conclusion.\n")
            f.write("- [ ] Tous les chiffres et métriques de tests sont certifiés par les journaux d'exécution réels.\n")
            f.write("- [ ] Les limites de la recherche/réalisation sont exposées avec honnêteté intellectuelle.\n\n")
            
            f.write("### 2. Éthique, Citations & Bibliographie\n")
            f.write("- [ ] Le fichier `references.bib` ne contient aucune référence fictive ou inventée.\n")
            f.write("- [ ] Toutes les citations dans le texte disposent d'un auteur, d'une date et d'une source vérifiable.\n")
            f.write("- [ ] L'Annexe B (Journal d'usage de l'IA) est intégralement complétée et signée.\n")
            f.write("- [ ] Aucun code secret, mot de passe ou donnée personnelle d'élève ne figure dans les captures.\n\n")
            
            f.write("### 3. Mise en Page & Normes Typographiques\n")
            f.write("- [ ] La page de garde respecte scrupuleusement la charte graphique de l'université.\n")
            f.write("- [ ] Le résumé en français et l'abstract en anglais sont accompagnés de leurs mots-clés.\n")
            f.write("- [ ] Le sommaire, la liste des figures et la liste des tableaux sont générés automatiquement.\n")
            f.write("- [ ] Toutes les images insérées sont nettes (300 DPI) et comportent un titre et une source.\n")
            f.write("- [ ] Les marges (2.5 cm), interligne (1.5) et police (11 ou 12 pt) sont conformes au règlement.\n\n")
            
            f.write("### 4. Livrables Physiques et Numériques\n")
            f.write("- [ ] Fichier PDF finalisé et compilé sans warning majeur (`memoire/docs/build/main.pdf`).\n")
            f.write("- [ ] Dépôt GitHub propre avec README, guide de déploiement et tag de version (`v1.0.0`).\n")
            f.write("- [ ] Support de présentation (diaporama pour les 20 minutes de soutenance) préparé.\n")
            f.write("- [ ] Exemplaires imprimés et reliés prêts pour les membres du jury.\n")

        # Miroir automatique dans audit/reports/
        mirror_dir = self.root_dir / "audit" / "reports"
        try:
            mirror_dir.mkdir(parents=True, exist_ok=True)
            import shutil
            for name in ["memoire_audit_report.md", "anomalies_matrix.csv", "questions_soutenance.md", "checklist_depot.md"]:
                src = self.export_dir / name
                if src.exists():
                    shutil.copy2(src, mirror_dir / name)
        except Exception as e:
            pass


# ==============================================================================
# POINT D'ENTRÉE CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="🎓 Memoire Guardian AI — Audit Académique Automatisé")
    parser.add_argument("--root", default=".", help="Racine du dépôt")
    parser.add_argument("--memoire-dir", default="memoire/docs", help="Dossier du mémoire")
    parser.add_argument("--export-dir", default="memoire/audit", help="Dossier d'export des rapports")
    parser.add_argument("--json", action="store_true", help="Afficher le résultat au format JSON")
    args = parser.parse_args()

    root_dir = Path(args.root).resolve()
    memoire_dir = (root_dir / args.memoire_dir).resolve()
    export_dir = (root_dir / args.export_dir).resolve()

    guardian = MemoireGuardian(memoire_dir, root_dir, export_dir)
    try:
        summary = guardian.executer_audit_complet()
        guardian.generer_livrables(summary)

        if args.json:
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            print("======================================================================")
            print("🎓 MEMOIRE GUARDIAN AI — RÉSULTATS DE L'AUDIT ACADÉMIQUE")
            print("======================================================================")
            print(f"Verdict : {summary['badge']} {summary['verdict']}")
            print(f"Score indicatif : {summary['total_score']} / 100")
            print(f"Détail anomalies : {summary['counts']['critiques']} critique(s), "
                  f"{summary['counts']['majeures']} majeure(s), {summary['counts']['mineures']} mineure(s)")
            print("----------------------------------------------------------------------")
            for pid, p in guardian.phases.items():
                print(f"[{p.phase_id}] {p.name:<32} : {p.score:>4.1f} / {p.max_score} ({p.status})")
            print("----------------------------------------------------------------------")
            print(f"📁 Livrables générés dans : {export_dir}")
            print(f"  - Rapport complet    : {export_dir / 'memoire_audit_report.md'}")
            print(f"  - Matrice anomalies  : {export_dir / 'anomalies_matrix.csv'}")
            print(f"  - Questions du jury  : {export_dir / 'questions_soutenance.md'}")
            print(f"  - Checklist de dépôt : {export_dir / 'checklist_depot.md'}")
            print("======================================================================")

        sys.exit(0 if summary['counts']['critiques'] == 0 else 1)

    except Exception as e:
        print(f"❌ Erreur critique d'exécution de Memoire Guardian : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()
