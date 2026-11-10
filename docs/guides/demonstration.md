# 🎬 Guide de Démonstration & Scénario de Soutenance — École 221

## 1. Objectif de la Démonstration
Prouver devant le jury :
1. L'étanchéité multi-tenant stricte entre deux établissements scolaires indépendants.
2. Le cycle de vie complet d'une inscription scolaire et du paiement mobile associé.
3. La traçabilité DevSecOps et l'absence de failles d'isolation.

## 2. Déroulé Pas-à-Pas
1. **Étape 1 : Connexion Établissement A** (Lycée d'Excellence Dakar)
   - Identifiant : `admin.test@ecole221.sn`
   - Visualisation de la liste des élèves et des classes du Tenant A.
2. **Étape 2 : Tentative d'Accès Croisé (Test d'Isolation)**
   - Requête vers une ressource du Tenant B avec le token du Tenant A.
   - Constat du blocage (HTTP 404 / RFC 7807).
3. **Étape 3 : Consultation Côté Parent**
   - Identifiant : `parent.test@ecole221.sn`
   - Accès aux bulletins et échéancier de paiement uniquement pour ses enfants rattachés.
