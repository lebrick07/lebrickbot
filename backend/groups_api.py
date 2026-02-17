"""
Groups and Permissions API
Manage user groups and customer access control
"""
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from database import get_db
from database.models import User, Group, UserGroup, GroupCustomerAccess, UserCustomerAccess, Customer, AuditLog
from auth import get_current_user, require_admin


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GroupCreate(BaseModel):
    """Create a new group"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class GroupUpdate(BaseModel):
    """Update group details"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class GroupResponse(BaseModel):
    """Group with basic info"""
    id: int
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str
    member_count: int
    customer_count: int


class GroupDetailResponse(BaseModel):
    """Group with full details (members + customers)"""
    id: int
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str
    members: List[dict]  # [{id, email, username, first_name, last_name}]
    customers: List[dict]  # [{id, name}]


class AddMemberRequest(BaseModel):
    """Add user to group"""
    user_id: int


class AddCustomerAccessRequest(BaseModel):
    """Grant customer access to group"""
    customer_id: str


# ============================================================================
# ACCESS CONTROL HELPERS
# ============================================================================

def get_accessible_customers(db: Session, user: User) -> List[str]:
    """
    Get list of customer IDs this user can access
    
    Returns customer IDs from:
    1. Direct user access (UserCustomerAccess)
    2. Group-based access (via UserGroup → GroupCustomerAccess)
    """
    customer_ids = set()
    
    # Direct user access (highest priority)
    direct_access = db.query(UserCustomerAccess).filter(
        UserCustomerAccess.user_id == user.id
    ).all()
    customer_ids.update([access.customer_id for access in direct_access])
    
    # Group-based access
    user_groups = db.query(UserGroup).filter(
        UserGroup.user_id == user.id
    ).all()
    
    for ug in user_groups:
        group_access = db.query(GroupCustomerAccess).filter(
            GroupCustomerAccess.group_id == ug.group_id
        ).all()
        customer_ids.update([access.customer_id for access in group_access])
    
    return list(customer_ids)


def user_can_access_customer(db: Session, user: User, customer_id: str) -> bool:
    """Check if user has access to specific customer"""
    # Admins can access everything
    if user.role == 'admin':
        return True
    
    accessible = get_accessible_customers(db, user)
    return customer_id in accessible


# ============================================================================
# GROUP MANAGEMENT ENDPOINTS
# ============================================================================

def list_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List all groups (admin only)
    
    GET /api/v1/groups
    """
    groups = db.query(Group).all()
    
    result = []
    for group in groups:
        member_count = db.query(UserGroup).filter(UserGroup.group_id == group.id).count()
        customer_count = db.query(GroupCustomerAccess).filter(
            GroupCustomerAccess.group_id == group.id
        ).count()
        
        result.append({
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "created_at": group.created_at.isoformat(),
            "updated_at": group.updated_at.isoformat(),
            "member_count": member_count,
            "customer_count": customer_count
        })
    
    return result


def create_group(
    data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new group (admin only)
    
    POST /api/v1/groups
    Body: {name, description}
    """
    # Check if group name already exists
    existing = db.query(Group).filter(Group.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Group name already exists")
    
    # Create group
    group = Group(
        name=data.name,
        description=data.description
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="group_created",
        resource_type="group",
        resource_id=str(group.id),
        details={"name": group.name}
    )
    db.add(audit)
    db.commit()
    
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_at": group.created_at.isoformat(),
        "updated_at": group.updated_at.isoformat(),
        "member_count": 0,
        "customer_count": 0
    }


def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get group details with members and customers (admin only)
    
    GET /api/v1/groups/{group_id}
    """
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get members
    user_groups = db.query(UserGroup).filter(UserGroup.group_id == group_id).all()
    members = []
    for ug in user_groups:
        user = db.query(User).filter(User.id == ug.user_id).first()
        if user:
            members.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "added_at": ug.added_at.isoformat()
            })
    
    # Get customers
    group_customers = db.query(GroupCustomerAccess).filter(
        GroupCustomerAccess.group_id == group_id
    ).all()
    customers = []
    for gc in group_customers:
        customer = db.query(Customer).filter(Customer.id == gc.customer_id).first()
        if customer:
            customers.append({
                "id": customer.id,
                "name": customer.name,
                "granted_at": gc.granted_at.isoformat()
            })
    
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "created_at": group.created_at.isoformat(),
        "updated_at": group.updated_at.isoformat(),
        "members": members,
        "customers": customers
    }


def update_group(
    group_id: int,
    data: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update group details (admin only)
    
    PATCH /api/v1/groups/{group_id}
    Body: {name?, description?}
    """
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check for name conflicts
    if data.name and data.name != group.name:
        existing = db.query(Group).filter(Group.name == data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Group name already exists")
        group.name = data.name
    
    if data.description is not None:
        group.description = data.description
    
    group.updated_at = datetime.utcnow()
    db.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="group_updated",
        resource_type="group",
        resource_id=str(group.id),
        details=data.dict(exclude_none=True)
    )
    db.add(audit)
    db.commit()
    
    return group.to_dict()


def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete group (admin only)
    
    DELETE /api/v1/groups/{group_id}
    
    Cascades: Removes all UserGroup and GroupCustomerAccess entries
    """
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    group_name = group.name
    
    # Audit log before deletion
    audit = AuditLog(
        user_id=current_user.id,
        action="group_deleted",
        resource_type="group",
        resource_id=str(group.id),
        details={"name": group_name}
    )
    db.add(audit)
    
    # Delete group (cascades to UserGroup and GroupCustomerAccess)
    db.delete(group)
    db.commit()
    
    return {"message": f"Group '{group_name}' deleted successfully"}


# ============================================================================
# GROUP MEMBERS ENDPOINTS
# ============================================================================

def add_group_member(
    group_id: int,
    data: AddMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Add user to group (admin only)
    
    POST /api/v1/groups/{group_id}/members
    Body: {user_id}
    """
    # Verify group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Verify user exists
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = db.query(UserGroup).filter(
        UserGroup.user_id == data.user_id,
        UserGroup.group_id == group_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already in group")
    
    # Add membership
    membership = UserGroup(
        user_id=data.user_id,
        group_id=group_id
    )
    db.add(membership)
    db.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="group_member_added",
        resource_type="group",
        resource_id=str(group_id),
        details={
            "group_name": group.name,
            "added_user_id": data.user_id,
            "added_user_email": user.email
        }
    )
    db.add(audit)
    db.commit()
    
    return {"message": f"User {user.email} added to group {group.name}"}


def remove_group_member(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Remove user from group (admin only)
    
    DELETE /api/v1/groups/{group_id}/members/{user_id}
    """
    # Verify group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Find membership
    membership = db.query(UserGroup).filter(
        UserGroup.user_id == user_id,
        UserGroup.group_id == group_id
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="User not in group")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    # Remove membership
    db.delete(membership)
    db.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="group_member_removed",
        resource_type="group",
        resource_id=str(group_id),
        details={
            "group_name": group.name,
            "removed_user_id": user_id,
            "removed_user_email": user.email if user else None
        }
    )
    db.add(audit)
    db.commit()
    
    return {"message": f"User removed from group {group.name}"}


# ============================================================================
# GROUP CUSTOMER ACCESS ENDPOINTS
# ============================================================================

def add_group_customer_access(
    group_id: int,
    data: AddCustomerAccessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Grant customer access to group (admin only)
    
    POST /api/v1/groups/{group_id}/customers
    Body: {customer_id}
    """
    # Verify group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if already granted
    existing = db.query(GroupCustomerAccess).filter(
        GroupCustomerAccess.group_id == group_id,
        GroupCustomerAccess.customer_id == data.customer_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer access already granted")
    
    # Grant access
    access = GroupCustomerAccess(
        group_id=group_id,
        customer_id=data.customer_id
    )
    db.add(access)
    db.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="group_customer_access_granted",
        resource_type="group",
        resource_id=str(group_id),
        details={
            "group_name": group.name,
            "customer_id": data.customer_id,
            "customer_name": customer.name
        }
    )
    db.add(audit)
    db.commit()
    
    return {"message": f"Customer '{customer.name}' access granted to group {group.name}"}


def remove_group_customer_access(
    group_id: int,
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Revoke customer access from group (admin only)
    
    DELETE /api/v1/groups/{group_id}/customers/{customer_id}
    """
    # Verify group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Find access grant
    access = db.query(GroupCustomerAccess).filter(
        GroupCustomerAccess.group_id == group_id,
        GroupCustomerAccess.customer_id == customer_id
    ).first()
    if not access:
        raise HTTPException(status_code=404, detail="Customer access not found")
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    # Revoke access
    db.delete(access)
    db.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="group_customer_access_revoked",
        resource_type="group",
        resource_id=str(group_id),
        details={
            "group_name": group.name,
            "customer_id": customer_id,
            "customer_name": customer.name if customer else None
        }
    )
    db.add(audit)
    db.commit()
    
    return {"message": f"Customer access revoked from group {group.name}"}


# ============================================================================
# USER CUSTOMER ACCESS (DIRECT) ENDPOINTS
# ============================================================================

def add_user_customer_access(
    user_id: int,
    data: AddCustomerAccessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Grant direct customer access to user (admin only)
    
    POST /api/v1/users/{user_id}/customers
    Body: {customer_id}
    
    Direct access overrides group-based access
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if already granted
    existing = db.query(UserCustomerAccess).filter(
        UserCustomerAccess.user_id == user_id,
        UserCustomerAccess.customer_id == data.customer_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer access already granted")
    
    # Grant access
    access = UserCustomerAccess(
        user_id=user_id,
        customer_id=data.customer_id
    )
    db.add(access)
    db.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="user_customer_access_granted",
        resource_type="user",
        resource_id=str(user_id),
        details={
            "user_email": user.email,
            "customer_id": data.customer_id,
            "customer_name": customer.name
        }
    )
    db.add(audit)
    db.commit()
    
    return {"message": f"Customer '{customer.name}' access granted to user {user.email}"}


def remove_user_customer_access(
    user_id: int,
    customer_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Revoke direct customer access from user (admin only)
    
    DELETE /api/v1/users/{user_id}/customers/{customer_id}
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find access grant
    access = db.query(UserCustomerAccess).filter(
        UserCustomerAccess.user_id == user_id,
        UserCustomerAccess.customer_id == customer_id
    ).first()
    if not access:
        raise HTTPException(status_code=404, detail="Customer access not found")
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    # Revoke access
    db.delete(access)
    db.commit()
    
    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="user_customer_access_revoked",
        resource_type="user",
        resource_id=str(user_id),
        details={
            "user_email": user.email,
            "customer_id": customer_id,
            "customer_name": customer.name if customer else None
        }
    )
    db.add(audit)
    db.commit()
    
    return {"message": f"Customer access revoked from user {user.email}"}
