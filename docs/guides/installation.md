# 🛠️ Guide d'Installation & Déploiement Reproductible — École 221

## 1. Pré-requis Système
- Linux / macOS (ou WSL2 sous Windows)
- Docker & Docker Compose v2+
- Java 17 (OpenJDK / Temurin)
- Node.js 18+ & npm 9+
- PostgreSQL 15 (si exécution locale hors conteneur)

## 2. Démarrage Rapide (Docker)
```bash
# 1. Cloner le dépôt avec ses sous-modules
git clone --recurse-submodules <url-du-depot>
cd "bou bakh"

# 2. Configurer les variables d'environnement
cp backend/.env.example backend/.env

# 3. Démarrer l'infrastructure et l'API
./orchestrator.sh up
```

## 3. Chargement des Données de Test (Fixtures)
```bash
./orchestrator.sh fixtures
```
Comptes initialisés :
- Super-Admin : `admin.test@ecole221.sn`
- Parent : `parent.test@ecole221.sn`
- Établissement B (Tenant B) : `admin.tenantb@ecole221.sn`

## 4. Vérification de la Santé du Système
```bash
./orchestrator.sh test
./orchestrator.sh check-agents
```
