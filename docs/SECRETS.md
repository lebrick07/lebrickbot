# Secret Management for OpenLuffy

## Overview

OpenLuffy requires API keys for external services:
- **Anthropic Claude API** - For intelligent AI agent

These secrets are:
1. Stored in GitHub Secrets (encrypted)
2. Automatically created in K8s by release pipelines
3. Referenced by deployments as environment variables

---

## Setup Process (One Time)

### 1. Add Secret to GitHub

**Go to:** https://github.com/lebrick07/openluffy/settings/secrets/actions

**Click:** "New repository secret"

**Name:** `ANTHROPIC_API_KEY`
**Value:** `sk-ant-api03-...` (your Claude API key)

---

### 2. Set Up Self-Hosted Runner

**Required for automation to work:**

See: [docs/GITHUB_RUNNER.md](./GITHUB_RUNNER.md)

The runner allows workflows to access kubectl and create K8s secrets automatically.

---

### 3. Deploy

**Secrets are created automatically by release pipelines!**

When you merge to `develop`:
- Release-Dev workflow runs
- Creates `openluffy-dev-api-keys` in `openluffy-dev` namespace
- Creates `openluffy-preprod-api-keys` in `openluffy-preprod` namespace
- Uses `${{ secrets.ANTHROPIC_API_KEY }}` from GitHub

When you merge to `main`:
- Release-Prod workflow runs
- Creates `openluffy-prod-api-keys` in `openluffy-prod` namespace

**No manual kubectl commands needed!**

---

### 3. Verify Secrets

```bash
# Check secret exists
kubectl get secret openluffy-dev-api-keys -n openluffy-dev

# View secret (base64 encoded)
kubectl get secret openluffy-dev-api-keys -n openluffy-dev -o yaml

# Decode and check (for debugging)
kubectl get secret openluffy-dev-api-keys -n openluffy-dev \
  -o jsonpath='{.data.claude-api-key}' | base64 -d | head -c 20
```

---

## How Deployments Use Secrets

The backend deployment references the secret:

```yaml
env:
  - name: ANTHROPIC_API_KEY
    valueFrom:
      secretKeyRef:
        name: {{ .Release.Name }}-api-keys  # e.g., openluffy-dev-api-keys
        key: claude-api-key
        optional: false
```

When pods start, the secret value is injected as an environment variable.

---

## Updating Secrets

To update a secret (e.g., API key rotation):

```bash
# Export new key
export ANTHROPIC_API_KEY=sk-ant-new-key...

# Update secret (same command as create)
./scripts/create-secrets.sh all

# Restart pods to pick up new secret
kubectl rollout restart deployment openluffy-dev-backend -n openluffy-dev
kubectl rollout restart deployment openluffy-preprod-backend -n openluffy-preprod
kubectl rollout restart deployment openluffy-prod-backend -n openluffy-prod
```

---

## Security Best Practices

**✅ DO:**
- Store API keys in GitHub Secrets (encrypted at rest)
- Use K8s secrets (never plain text in config files)
- Rotate keys periodically
- Use different keys for dev/prod (if budget allows)
- Limit key permissions to minimum required

**❌ DON'T:**
- Commit API keys to git (even in private repos)
- Share keys in Slack/email
- Use prod keys in dev environments
- Store keys in environment files (.env committed to git)

---

## Future Improvements

For production-grade secret management, consider:

1. **Sealed Secrets** - Encrypt secrets and commit to git
2. **External Secrets Operator** - Pull from AWS Secrets Manager / Vault
3. **SOPS** - Encrypt files with age/pgp keys
4. **GitHub OIDC** - Automated secret injection from GitHub Actions

For now, the script-based approach balances security and simplicity.

---

## Troubleshooting

**Pod fails with "API key not configured":**
```bash
# Check if secret exists
kubectl get secret openluffy-dev-api-keys -n openluffy-dev

# If missing, create it
export ANTHROPIC_API_KEY=sk-ant-...
./scripts/create-secrets.sh dev
```

**Pod doesn't pick up new secret:**
```bash
# Secrets aren't hot-reloaded, restart pods
kubectl rollout restart deployment openluffy-dev-backend -n openluffy-dev
```

**Secret exists but pod still fails:**
```bash
# Check deployment references correct secret name
kubectl get deployment openluffy-dev-backend -n openluffy-dev -o yaml | grep -A5 ANTHROPIC_API_KEY

# Check pod logs for error details
kubectl logs -n openluffy-dev -l app=openluffy-dev-backend
```

---

**For questions:** See main README or ask in Discord: https://discord.com/invite/clawd
