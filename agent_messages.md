# 📬 Agent Message Bus — Communication & Coordination Inter-Agents

> **Fichier central de communication et de synchronisation asynchrone du framework agentique.**
> Ce fichier permet à tous les agents spécialisés (Agents 00 à 11) de publier leurs annonces, d'échanger des contrats et de tracer les livrables avec statut (`PENDING` / `DONE`).
> **NE PAS SUPPRIMER.**

---

## 📖 Protocole de Communication du Bus

1. **Cycle Backend ↔ Frontend** :
   - L'agent **Backend** implémente une API ou modifie un endpoint existant.
   - Il publie un message dans `## 📤 Messages du Backend → Frontend` avec `Status: PENDING`.
   - L'agent **Frontend** intègre l'API, effectue le build, puis bascule le statut à `Status: DONE ✅`.

2. **Cycle Qualification & Sécurité** :
   - L'agent **QA** valide chaque suite de tests d'intégration et consigne les assertions dans le bus.
   - L'agent **DevSecOps** audite les dépendances et la configuration Docker.

3. **Gouvernance & Supervision Kasongo** :
   - L'agent **00 (Kasongo)** contrôle la livraison (`./orchestrator.sh handover <agent>`).
   - Le **Tech Lead humain** émet l'approbation formelle finale avant fusion (`git merge`).

---

## 📤 Messages du Backend → Frontend

_Aucun message en attente._

---

## 📥 Messages du Frontend → Backend (Feedback & Demandes API)

_Aucun message en attente._

---

## 🛡️ Messages DevSecOps & Assurance Qualité

_Aucun message en attente._

---

## 📋 Messages de Clôture & Supervision

_Aucun message en attente._
