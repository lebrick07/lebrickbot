# Self-Hosted GitHub Actions Runner on Pi

## Why We Need This

Our release pipelines need to create K8s secrets automatically. GitHub's cloud runners can't access your Pi's K8s cluster, so we need a self-hosted runner.

---

## One-Time Setup

### 1. Install Runner on Pi

**Go to:** https://github.com/lebrick07/openluffy/settings/actions/runners/new

**Select:**
- Runner image: Linux
- Architecture: ARM64

**Follow the commands shown:**

```bash
# Create runner directory
mkdir -p ~/actions-runner && cd ~/actions-runner

# Download ARM64 runner
curl -o actions-runner-linux-arm64-2.313.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.313.0/actions-runner-linux-arm64-2.313.0.tar.gz

# Extract
tar xzf ./actions-runner-linux-arm64-2.313.0.tar.gz

# Configure
./config.sh --url https://github.com/lebrick07/openluffy --token <TOKEN_FROM_GITHUB>

# When prompted:
# - Runner name: pi5-lebrickbot
# - Runner group: Default
# - Labels: self-hosted,Linux,ARM64,pi
# - Work folder: _work

# Install as a service
sudo ./svc.sh install
sudo ./svc.sh start
```

---

### 2. Verify Runner

**Check status:**
```bash
sudo ./svc.sh status
```

**Should see:**
```
● actions.runner.lebrick07-openluffy.pi5-lebrickbot.service - GitHub Actions Runner
   Active: active (running)
```

**In GitHub:**
- Go to: https://github.com/lebrick07/openluffy/settings/actions/runners
- Should see: "pi5-lebrickbot" with green "Idle" status

---

### 3. Label Workflows to Use Self-Hosted Runner

Our release workflows will use:
```yaml
runs-on: self-hosted
```

This ensures they run on the Pi where kubectl works.

---

## How It Works

**Release-Dev Workflow:**
1. Runs on self-hosted runner (Pi)
2. Builds Docker images (multi-arch)
3. Pushes to ghcr.io
4. **Creates K8s secret** using `${{ secrets.ANTHROPIC_API_KEY }}`
5. Updates Helm values
6. Commits changes
7. ArgoCD syncs automatically

**Release-Prod Workflow:**
- Same flow, but for production

**Secrets are created automatically** - no manual kubectl needed!

---

## Security Considerations

**✅ Secure because:**
- Runner runs as non-root user
- Only runs workflows from your repo
- Has access to secrets via GitHub
- kubectl access is limited to Pi's kubeconfig

**❌ Don't:**
- Run untrusted code on the runner
- Give the runner admin access to the host

---

## Troubleshooting

**Runner offline:**
```bash
cd ~/actions-runner
sudo ./svc.sh status
sudo ./svc.sh start
```

**Workflow fails with "kubectl: command not found":**
```bash
# Ensure kubectl is in PATH for runner user
which kubectl
sudo ln -s /usr/local/bin/k3s /usr/local/bin/kubectl
```

**Secret creation fails:**
```bash
# Test kubectl access as runner user
sudo -u $(whoami) kubectl get namespaces
```

---

## Alternative: Cloud Runner with kubeconfig

If you don't want a self-hosted runner, you can:
1. Export kubeconfig: `sudo k3s kubectl config view --raw > kubeconfig.yaml`
2. Add as GitHub secret: `KUBECONFIG_DATA`
3. Workflows decode and use it

**⚠️ Security risk:** kubeconfig has full cluster access. Self-hosted runner is safer.

---

**Recommended: Use self-hosted runner for secure, automated secret management.**
