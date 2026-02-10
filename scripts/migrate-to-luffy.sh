#!/bin/bash
# Migrate from lebrickbot to luffy infrastructure

set -e

echo "🏴‍☠️ Migrating infrastructure: lebrickbot → luffy"
echo ""

# Step 1: Delete old ArgoCD application
echo "1️⃣ Deleting old ArgoCD application 'lebrickbot'..."
kubectl delete application lebrickbot -n argocd 2>/dev/null || echo "   (Application already deleted or doesn't exist)"

# Step 2: Delete old namespace (this will delete all pods/deployments)
echo "2️⃣ Deleting old namespace 'lebrickbot'..."
kubectl delete namespace lebrickbot 2>/dev/null || echo "   (Namespace already deleted or doesn't exist)"

# Wait for namespace to be fully deleted
echo "   Waiting for namespace deletion to complete..."
while kubectl get namespace lebrickbot 2>/dev/null; do
  echo -n "."
  sleep 2
done
echo ""
echo "   ✓ Namespace deleted"

# Step 3: Delete old RBAC resources (if they exist outside namespace)
echo "3️⃣ Cleaning up old RBAC resources..."
kubectl delete clusterrole lebrickbot-backend-cluster-role 2>/dev/null || echo "   (ClusterRole already deleted)"
kubectl delete clusterrolebinding lebrickbot-backend-cluster-role-binding 2>/dev/null || echo "   (ClusterRoleBinding already deleted)"

# Step 4: Apply new ArgoCD application
echo "4️⃣ Creating new ArgoCD application 'luffy'..."
kubectl apply -f argocd/luffy-application.yaml

echo ""
echo "✅ Migration complete!"
echo ""
echo "ArgoCD will now:"
echo "  • Create namespace 'luffy'"
echo "  • Deploy luffy-backend and luffy-frontend"
echo "  • Create ingress at http://openluffy.local"
echo ""
echo "Monitor deployment:"
echo "  kubectl get pods -n luffy -w"
echo ""
echo "⚠️  Don't forget to update /etc/hosts:"
echo "  sudo sed -i 's/openbrick.local/openluffy.local/g' /etc/hosts"
echo "  or manually add: 192.168.1.10 openluffy.local"
