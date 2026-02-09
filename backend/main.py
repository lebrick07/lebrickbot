from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import re
from datetime import datetime

app = FastAPI(title="lebrickbot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_kubectl(cmd):
    """Run kubectl command and return output"""
    try:
        result = subprocess.run(
            ["sudo", "kubectl"] + cmd.split(),
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/")
def root():
    return {"service": "lebrickbot", "status": "running", "version": "0.1.0"}

@app.get("/api/status")
def api_status():
    return {
        "service": "lebrickbot-backend",
        "status": "operational",
        "version": "0.1.0"
    }

@app.get("/api/customers")
def get_customers():
    """Get all customer deployments"""
    customers = []
    
    # Acme Corp
    acme_pods = run_kubectl("get pods -n acme-corp -o json")
    try:
        acme_data = json.loads(acme_pods)
        acme_replicas = len([p for p in acme_data.get('items', []) if p['status']['phase'] == 'Running'])
        acme_status = 'running' if acme_replicas > 0 else 'error'
    except:
        acme_replicas = 0
        acme_status = 'error'
    
    customers.append({
        'id': 'acme-corp',
        'name': 'Acme Corp',
        'app': 'acme-corp-api',
        'stack': 'Node.js',
        'status': acme_status,
        'replicas': acme_replicas,
        'namespace': 'acme-corp',
        'url': 'http://acme.local',
        'endpoints': ['/health', '/products', '/orders']
    })
    
    # TechStart
    techstart_pods = run_kubectl("get pods -n techstart -o json")
    try:
        techstart_data = json.loads(techstart_pods)
        techstart_replicas = len([p for p in techstart_data.get('items', []) if p['status']['phase'] == 'Running'])
        techstart_status = 'running' if techstart_replicas > 0 else 'error'
    except:
        techstart_replicas = 0
        techstart_status = 'error'
    
    customers.append({
        'id': 'techstart',
        'name': 'TechStart Inc',
        'app': 'techstart-webapp',
        'stack': 'Python FastAPI',
        'status': techstart_status,
        'replicas': techstart_replicas,
        'namespace': 'techstart',
        'url': 'http://techstart.local',
        'endpoints': ['/health', '/metrics', '/analytics', '/users']
    })
    
    # WidgetCo
    widgetco_pods = run_kubectl("get pods -n widgetco -o json")
    try:
        widgetco_data = json.loads(widgetco_pods)
        widgetco_replicas = len([p for p in widgetco_data.get('items', []) if p['status']['phase'] == 'Running'])
        widgetco_status = 'running' if widgetco_replicas > 0 else 'error'
    except:
        widgetco_replicas = 0
        widgetco_status = 'error'
    
    customers.append({
        'id': 'widgetco',
        'name': 'WidgetCo Manufacturing',
        'app': 'widgetco-api',
        'stack': 'Go',
        'status': widgetco_status,
        'replicas': widgetco_replicas,
        'namespace': 'widgetco',
        'url': 'http://widgetco.local',
        'endpoints': ['/health', '/inventory', '/suppliers']
    })
    
    return {'customers': customers, 'total': len(customers)}

@app.get("/api/argocd/apps")
def get_argocd_apps():
    """Get ArgoCD application status"""
    apps_output = run_kubectl("get applications -n argocd -o json")
    
    try:
        apps_data = json.loads(apps_output)
        apps = []
        
        for app in apps_data.get('items', []):
            name = app['metadata']['name']
            if name in ['acme-corp-api', 'techstart-webapp', 'widgetco-api']:
                apps.append({
                    'name': name,
                    'sync_status': app.get('status', {}).get('sync', {}).get('status', 'Unknown'),
                    'health_status': app.get('status', {}).get('health', {}).get('status', 'Unknown'),
                    'repo': app['spec']['source']['repoURL'],
                    'path': app['spec']['source']['path'],
                    'namespace': app['spec']['destination']['namespace']
                })
        
        return {'apps': apps, 'total': len(apps)}
    except Exception as e:
        return {'error': str(e), 'apps': [], 'total': 0}

@app.get("/api/deployments")
def get_deployments():
    """Get all deployments across all customer namespaces"""
    deployments = []
    namespaces = ['acme-corp', 'techstart', 'widgetco']
    
    for ns in namespaces:
        deploy_output = run_kubectl(f"get deployments -n {ns} -o json")
        
        try:
            deploy_data = json.loads(deploy_output)
            
            for deploy in deploy_data.get('items', []):
                name = deploy['metadata']['name']
                replicas = deploy['status'].get('replicas', 0)
                ready = deploy['status'].get('readyReplicas', 0)
                
                deployments.append({
                    'id': f"{ns}-{name}",
                    'name': name,
                    'namespace': ns,
                    'customer': ns.replace('-', ' ').title(),
                    'replicas': replicas,
                    'ready': ready,
                    'status': 'running' if ready == replicas else 'degraded',
                    'image': deploy['spec']['template']['spec']['containers'][0]['image']
                })
        except:
            pass
    
    return {'deployments': deployments, 'total': len(deployments)}
