from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any

from libs.infrastructure.database.session import get_db
from libs.infrastructure.database.models import Tenant, User, UserRole
from libs.common.auth.security import hash_password
from libs.common.auth.jwt import create_access_token

router = APIRouter()

class OnboardRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)

class OnboardResponse(BaseModel):
    tenant_id: str
    user_id: str
    email: str
    access_token: str
    token_type: str = "bearer"

@router.post("/onboard", response_model=OnboardResponse, status_code=status.HTTP_201_CREATED)
async def onboard_tenant(req: OnboardRequest, db: AsyncSession = Depends(get_db)):
    """Atomically create a tenant and its primary tenant admin user."""
    # Check if user already exists
    result = await db.execute(select(User).filter(User.email == req.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    try:
        # 1. Create Tenant
        new_tenant = Tenant(name=req.company_name)
        db.add(new_tenant)
        await db.flush()  # Flushes to get new_tenant.id

        # 2. Create Tenant Admin User
        hashed_pwd = hash_password(req.password)
        new_user = User(
            tenant_id=new_tenant.id,
            email=req.email,
            hashed_password=hashed_pwd,
            full_name=req.full_name,
            role=UserRole.TENANT_ADMIN,
            is_active=True
        )
        db.add(new_user)
        await db.flush()  # Flushes to get new_user.id
        
        # 3. Create Access Token
        token = create_access_token(
            subject=new_user.id,
            role=new_user.role.value,
            tenant_id=new_tenant.id
        )

        await db.commit()

        return OnboardResponse(
            tenant_id=new_tenant.id,
            user_id=new_user.id,
            email=new_user.email,
            access_token=token
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to onboard tenant due to database error: {str(e)}"
        )
