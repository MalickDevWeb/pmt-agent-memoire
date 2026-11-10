# 🎤 PRÉPARATION À LA SOUTENANCE ORALE DU MÉMOIRE

Ce guide recense les 10 questions critiques les plus probables posées par les membres du jury (Président, Rapporteur, Encadreur) et fournit les éléments factuels pour défendre vos travaux avec brio.

### 1. Sur l'isolation Multi-Tenant et la Sécurité (SEC-003)
**Question :** *« Comment garantissez-vous qu'une école A ne puisse jamais accéder par effraction ou injection aux données d'une école B ? »*

**Éléments de réponse recommandée :**
Défense : Expliquer que l'isolation ne repose pas sur un simple paramètre URL ou en-tête client (interdiction formelle du frontend d'envoyer X-Tenant-Id). L'isolation est garantie au niveau du token JWT signé, extrait côté backend par l'intercepteur de sécurité et injecté dans le contexte `@TenantId`. Chaque requête JPA applique automatiquement le filtre d'isolation sur la clé `organization_id`.

### 2. Sur le rôle et l'utilisation de l'Intelligence Artificielle
**Question :** *« Avez-vous rédigé ce mémoire vous-même ou s'agit-il d'un travail généré par ChatGPT ? »*

**Éléments de réponse recommandée :**
Défense : Présenter immédiatement l'Annexe B (Journal d'usage de l'IA). Démontrer que l'IA a agi comme un compilateur et un assistant d'orchestration (génération de squelettes et relecture), mais que chaque composant métier, règle de calcul et architecture logicielle provient des choix souverains de l'équipe étudiante et a été vérifié par des tests réels.

### 3. Sur l'Architecture Hexagonale et le DDD
**Question :** *« Pourquoi avoir choisi l'Architecture Hexagonale plutôt qu'une architecture classique en couches (Controller-Service-Repository) ? »*

**Éléments de réponse recommandée :**
Défense : Mettre en avant le découplage du domaine métier par rapport aux frameworks d'infrastructure (base de données, web REST). Cela permet de tester les cas d'utilisation métier de manière pure, sans dépendre d'un serveur applicatif ou d'une base Neon/Postgres démarrée.

### 4. Sur la Gouvernance de Projet et le framework Multi-Agents
**Question :** *« Qu'apporte concrètement un système multi-agents par rapport à un développement classique en équipe ? »*

**Éléments de réponse recommandée :**
Défense : Souligner la séparation stricte des responsabilités (RACI) et les garde-fous de qualité. Chaque agent (Architecte, QA, Sécurité, Dev) dispose de pré-requis et de livrables vérifiables par machine (check_agent_rules.py). Aucun code ne passe sans approbation de revue et tests d'intégration réussis.

### 5. Sur les Tests et la Qualification logicielle (Ch. 7)
**Question :** *« Quelle est la couverture réelle de vos tests et comment prouvez-vous le bon fonctionnement du système ? »*

**Éléments de réponse recommandée :**
Défense : Citer les chiffres exacts de l'audit : 16 modules testés, 142 assertions exécutées avec 100% de succès dans `logs/qa_execution.log`, validées par le rapport d'exécution de l'Agent 05. Mentionner les tests de non-régression et les scénarios de bout en bout.

### 6. Sur les Coûts et la Viabilité Financière (Ch. 5)
**Question :** *« Votre solution est-elle rentable pour un réseau d'établissements au Sénégal ? »*

**Éléments de réponse recommandée :**
Défense : Présenter le modèle économique à 120 000 FCFA/mois par école. Avec des coûts d'infrastructure cloud maîtrisés à 29,38 USD/mois (Neon + Render) et un coût unitaire par élève de 123 FCFA/an, le point mort est atteint dès 2 écoles abonnées.

### 7. Sur la Dette Technique et le Refactoring Frontend
**Question :** *« Avez-vous de la dette technique dans votre frontend React ? »*

**Éléments de réponse recommandée :**
Défense : Expliquer en toute franchise la stratégie de cliquet : nous avons traqué le typage strict (`any` réduit de 373 à 362) et migré les appels API directs vers TanStack React Query pour garantir un cache optimisé et zéro re-render inutile.

### 8. Sur la Résilience Réseau et le Mode Vigile Campus
**Question :** *« Comment le vigile contrôle-t-il les accès si la connexion Internet du campus tombe en panne ? »*

**Éléments de réponse recommandée :**
Défense : Expliquer le fonctionnement du mode déconnecté du vigile avec stockage local PWA/IndexedDB et signature cryptographique des badges QR, permettant une validation hors-ligne synchronisée ultérieurement dès le retour du réseau.

### 9. Sur la conformité RGPD / Protection des Données Personnelles
**Question :** *« Comment sont protégées les données sensibles des mineurs (élèves) et leurs bulletins scolaires ? »*

**Éléments de réponse recommandée :**
Défense : Citer le chiffrement des mots de passe avec BCrypt, les politiques RLS en base, l'absence de secrets dans les dépôts publics et le contrôle d'accès strict par rôle RBAC (seuls les parents et l'administration accèdent aux notes de l'élève).

### 10. Sur les Limites et les Perspectives d'Évolution
**Question :** *« Si vous deviez poursuivre ce travail en Master, quels chantiers engageriez-vous en priorité ? »*

**Éléments de réponse recommandée :**
Défense : Mentionner l'intégration d'un canal de paiement mobile money direct (Wave, Orange Money), le portage complet en application mobile native React Native pour les parents, et l'optimisation des requêtes complexes par une vue matérialisée CQRS.

