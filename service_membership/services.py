from .models import Membership
from sqlalchemy.orm import Session
from .schemas import MembershipBase
from datetime import datetime

def get_memberships(db: Session):
    """Retrieve all memberships from the database"""
    return db.query(Membership).all()

def get_membership_by_id(db: Session, membership_id: int):
    """Retrieve a membership by its ID"""
    return db.query(Membership).filter(Membership.membership_id == membership_id).first()

def create_membership(db: Session, membership: MembershipBase):
    """Create a new membership in the database"""
    
    # Parse datetime strings if provided, otherwise use current time
    start_date = membership.start_date
    if start_date is None:
        start_date = datetime.now()
    elif isinstance(start_date, str):
        # Handle both ISO format with 'Z' and without
        start_date = start_date.replace('Z', '+00:00')
        start_date = datetime.fromisoformat(start_date)
    
    end_date = membership.end_date
    if end_date and isinstance(end_date, str):
        end_date = end_date.replace('Z', '+00:00')
        end_date = datetime.fromisoformat(end_date)
    
    try:
        db_membership = Membership(
            user_id=membership.user_id,
            plan_type=membership.plan_type,
            payment_status=membership.payment_status,
            start_date=start_date,
            end_date=end_date,
            benefits=membership.benefits
        )
        db.add(db_membership)
        db.commit()
        db.refresh(db_membership)
        return db_membership
    except Exception as e:
        db.rollback()
        print(f"Database error: {str(e)}")
        raise