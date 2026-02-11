# {{CUSTOMER_NAME}} Application

Auto-generated application managed by OpenLuffy.

## Stack
- **Language**: {{STACK}}
- **Framework**: {{FRAMEWORK}}
- **Container Registry**: GitHub Container Registry (GHCR)

## Environments
- **Development**: `{{CUSTOMER_ID}}-dev` namespace
- **Pre-production**: `{{CUSTOMER_ID}}-preprod` namespace  
- **Production**: `{{CUSTOMER_ID}}-prod` namespace

## Local Development

### {{STACK_SETUP}}

## CI/CD Pipeline
GitHub Actions automatically builds and deploys on push:
- `develop` branch → DEV + PREPROD environments
- `main` branch → PRODUCTION environment (manual approval required)

## Deployment
Managed by ArgoCD - syncs automatically when new images are pushed.

## Health Check
All environments expose `/healthz` endpoint for liveness/readiness probes.

---
*Managed by OpenLuffy* 🏴‍☠️
