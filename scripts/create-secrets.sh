#!/bin/bash
#
# Create K8s secrets for OpenLuffy
#
# Usage:
#   export ANTHROPIC_API_KEY=sk-ant-...
#   ./scripts/create-secrets.sh [dev|preprod|prod|all]
#

set -e

ENV=${1:-all}

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ ANTHROPIC_API_KEY environment variable not set"
    echo ""
    echo "Usage:"
    echo "  export ANTHROPIC_API_KEY=sk-ant-..."
    echo "  ./scripts/create-secrets.sh [dev|preprod|prod|all]"
    exit 1
fi

create_secret() {
    local namespace=$1
    local secret_name="${namespace}-api-keys"
    
    echo "Creating secret in namespace: $namespace"
    
    kubectl create secret generic "$secret_name" \
        --from-literal=claude-api-key="$ANTHROPIC_API_KEY" \
        -n "$namespace" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    echo "✅ Secret $secret_name created/updated in $namespace"
}

if [ "$ENV" == "all" ] || [ "$ENV" == "dev" ]; then
    create_secret "openluffy-dev"
fi

if [ "$ENV" == "all" ] || [ "$ENV" == "preprod" ]; then
    create_secret "openluffy-preprod"
fi

if [ "$ENV" == "all" ] || [ "$ENV" == "prod" ]; then
    create_secret "openluffy-prod"
fi

echo ""
echo "🏴‍☠️ All secrets created successfully!"
echo ""
echo "Pods will restart automatically to pick up the new secret."
