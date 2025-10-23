from fastapi import APIRouter, Depends, status

from ..core.dependencies import get_current_user_id
from ..core.mongodb import get_database
from ..dto.customer_dto import CustomerProfileCreate, CustomerProfileResponse, CustomerProfileUpdate
from ..services.customer_profile_service import CustomerProfileService

router = APIRouter(prefix="/customer/profile", tags=["Customer Profile"])


@router.post("/", response_model=CustomerProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_customer_profile(
    data: CustomerProfileCreate, user_id: int = Depends(get_current_user_id), db=Depends(get_database)
):
    """创建客户资料"""
    service = CustomerProfileService(db)
    profile = await service.create_profile(
        user_id=user_id, location=data.location, address=data.address, budget_preference=data.budget_preference
    )
    return CustomerProfileResponse(**profile.model_dump())


@router.get("/me", response_model=CustomerProfileResponse)
async def get_my_customer_profile(user_id: int = Depends(get_current_user_id), db=Depends(get_database)):
    """获取当前用户的客户资料"""
    service = CustomerProfileService(db)
    profile = await service.get_profile(user_id)
    return CustomerProfileResponse(**profile.model_dump())


@router.put("/me", response_model=CustomerProfileResponse)
async def update_my_customer_profile(
    data: CustomerProfileUpdate, user_id: int = Depends(get_current_user_id), db=Depends(get_database)
):
    """更新当前用户的客户资料"""
    service = CustomerProfileService(db)
    profile = await service.update_profile(user_id=user_id, update_data=data.model_dump(exclude_unset=True))
    return CustomerProfileResponse(**profile.model_dump())


@router.get("/{user_id}", response_model=CustomerProfileResponse)
async def get_customer_profile_by_id(user_id: int, db=Depends(get_database)):
    """根据用户 ID 获取客户资料（公开接口）"""
    service = CustomerProfileService(db)
    profile = await service.get_profile(user_id)
    return CustomerProfileResponse(**profile.model_dump())
