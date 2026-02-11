"""
Initialize GitHub integrations for all customers on startup
Run this once to configure GitHub integrations if they don't exist
"""
import os
import httpx
from database import get_db, Integration
from sqlalchemy.orm import Session

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_ORG = os.getenv('GITHUB_ORG', 'lebrick07')

# Customer → GitHub repo mapping
CUSTOMER_REPOS = {
    'acme-corp': 'acme-corp-api',
    'openluffy': 'openluffy',
    'philly-cheese-corp': 'philly-cheese-corp',
    'techstart': 'techstart-webapp',
    'widgetco': 'widgetco-api',
}

def init_github_integrations(db: Session) -> None:
    """Initialize GitHub integrations for all customers if not already configured"""
    
    if not GITHUB_TOKEN:
        print("⚠️ GITHUB_TOKEN not set - skipping GitHub integration initialization")
        return
    
    print("🔧 Initializing GitHub integrations...")
    
    for customer_id, repo_name in CUSTOMER_REPOS.items():
        try:
            # Check if integration already exists
            existing = db.query(Integration).filter(
                Integration.customer_id == customer_id,
                Integration.type == 'github'
            ).first()
            
            if existing:
                print(f"   ✓ {customer_id} → GitHub already configured")
                continue
            
            # Create new GitHub integration
            config = {
                'org': GITHUB_ORG,
                'repo': repo_name,
                'token': GITHUB_TOKEN,
                'branch': 'main',
                'enabled': True
            }
            
            integration = Integration(
                customer_id=customer_id,
                type='github',
                config=config
            )
            db.add(integration)
            db.commit()
            
            print(f"   ✅ {customer_id} → {GITHUB_ORG}/{repo_name} configured")
            
        except Exception as e:
            print(f"   ❌ Failed to configure {customer_id}: {e}")
            db.rollback()
    
    print("✅ GitHub integrations initialization complete")

if __name__ == '__main__':
    # For manual testing
    from database import SessionLocal
    db = SessionLocal()
    try:
        init_github_integrations(db)
    finally:
        db.close()
