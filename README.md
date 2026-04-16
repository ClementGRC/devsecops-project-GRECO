# DevSecOps Pipeline — Projet 5DVSCOPS

Pipeline CI/CD sécurisé avec GitHub Actions intégrant des outils de scan de vulnérabilités, d'analyse de dépendances et de vérification de politiques de sécurité.

## Objectif du projet

Ce projet met en œuvre un pipeline DevSecOps complet autour d'une API Flask conteneurisée. Il intègre :

- Linting des fichiers YAML et du Dockerfile
- Build d'image Docker
- Scan des dépendances Python avec Trivy
- Scan de l'image Docker avec Trivy
- Vérification de politiques de sécurité Kubernetes avec Conftest (OPA Rego)

## Structure du projet

```
devsecops-project/
├── .github/workflows/ci.yml     # Pipeline GitHub Actions (5 jobs)
├── app/app.py                    # API Flask
├── k8s/
│   ├── deployment.yaml           # Manifeste K8s (vulnérable - runAsUser: 0)
│   └── deployment-fixed.yaml     # Manifeste K8s (corrigé)
├── policy/deny_root.rego         # Politique Conftest (3 règles Rego)
├── screenshots/                  # Rapports de scan enregistrés
├── Dockerfile                    # Image Docker de l'API
├── requirements.txt              # Dépendances Python
├── .yamllint.yml                 # Configuration yamllint
├── README.md
└── Rapport_Projet_DevSecOps.docx # Rapport final
```

## Architecture du pipeline

Le workflow CI/CD s'exécute en 5 jobs parallélisés :

| Job | Outil | Rôle |
|-----|-------|------|
| `lint` | yamllint + Hadolint | Vérification syntaxique des YAML et du Dockerfile |
| `build` | Docker | Construction de l'image conteneur (sauvegardée en artifact) |
| `trivy-fs-scan` | Trivy (fs) | Scan des dépendances Python (requirements.txt) |
| `trivy-image-scan` | Trivy (image) | Scan de l'image Docker (OS Debian + packages) |
| `conftest` | OPA / Rego | Vérification des politiques de sécurité K8s |

Dépendances entre jobs :
- `build`, `trivy-fs-scan`, `conftest` dépendent de `lint`
- `trivy-image-scan` dépend de `build`

## Utilisation locale

### Exécuter l'application

```bash
# Build
docker build -t devsecops-api .

# Run
docker run -p 5000:5000 devsecops-api

# Test
curl http://localhost:5000/health
# {"status":"healthy"}

curl http://localhost:5000/items
# {"count":4,"items":[...]}
```

### Exécuter les scans en local

```bash
# Installation de Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Scan des dépendances
trivy fs --scanners vuln --severity CRITICAL,HIGH,MEDIUM requirements.txt

# Scan de l'image
trivy image --severity CRITICAL,HIGH python:3.11-slim

# Installation de Conftest
wget https://github.com/open-policy-agent/conftest/releases/download/v0.56.0/conftest_0.56.0_Linux_x86_64.tar.gz
tar xzf conftest_0.56.0_Linux_x86_64.tar.gz

# Test de la politique
./conftest test k8s/deployment.yaml -p policy/         # FAIL attendu (runAsUser: 0)
./conftest test k8s/deployment-fixed.yaml -p policy/   # PASS attendu
```

## Politique de sécurité

La règle Conftest (`policy/deny_root.rego`) contient trois règles :

| Règle | Type | Condition |
|-------|------|-----------|
| `deny` (1) | Bloquant | Refuse si `runAsUser: 0` |
| `deny` (2) | Bloquant | Refuse si `runAsNonRoot: false` |
| `warn` | Avertissement | Alerte si pas de `securityContext` défini |

## Résumé des findings de sécurité

Résultats des scans effectués avec Trivy 0.69.3 et Conftest 0.56.0 :

| Scan | Vulnérabilités | Détail |
|------|----------------|--------|
| Trivy FS (requirements.txt) | 16 | 3 HIGH, 13 MEDIUM |
| Trivy Image (python:3.11-slim) | 49 | 12 HIGH, reste MEDIUM/LOW |
| Conftest (deployment.yaml) | 2 FAIL | runAsUser: 0 et runAsNonRoot: false |
| Conftest (deployment-fixed.yaml) | 0 | Tous tests passent |

Détails complets dans `Rapport_Projet_DevSecOps.docx`.

## Auteur

Projet réalisé dans le cadre du module 5DVSCOPS à l'ESTIAM (2025/2026).
