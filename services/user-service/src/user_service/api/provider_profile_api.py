from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status

from ..core.dependencies import get_current_user_id
from ..core.mongodb import get_database
from ..dto.provider_dto import ProviderProfileCreate, ProviderProfileResponse, ProviderProfileUpdate
from ..services.provider_profile_service import ProviderProfileService

router = APIRouter(prefix="/provider/profile", tags=["Provider Profile"])


@router.post("/", response_model=ProviderProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_provider_profile(
    data: ProviderProfileCreate, user_id: int = Depends(get_current_user_id), db=Depends(get_database)
):
    """创建服务商资料"""
    service = ProviderProfileService(db)
    profile = await service.create_profile(
        user_id=user_id,
        skills=data.skills,
        experience_years=data.experience_years,
        hourly_rate=data.hourly_rate,
        availability=data.availability,
    )
    return ProviderProfileResponse(**profile.model_dump())


@router.get("/me", response_model=ProviderProfileResponse)
async def get_my_provider_profile(user_id: int = Depends(get_current_user_id), db=Depends(get_database)):
    """获取当前用户的服务商资料"""
    service = ProviderProfileService(db)
    profile = await service.get_profile(user_id)
    return ProviderProfileResponse(**profile.model_dump())


@router.put("/me", response_model=ProviderProfileResponse)
async def update_my_provider_profile(
    data: ProviderProfileUpdate, user_id: int = Depends(get_current_user_id), db=Depends(get_database)
):
    """更新当前用户的服务商资料"""
    service = ProviderProfileService(db)
    profile = await service.update_profile(user_id=user_id, update_data=data.model_dump(exclude_unset=True))
    return ProviderProfileResponse(**profile.model_dump())


@router.get("/search", response_model=List[ProviderProfileResponse])
async def search_providers(
    skills: Optional[List[str]] = Query(default=None),
    min_rating: Optional[float] = Query(default=None, ge=0, le=5),
    max_hourly_rate: Optional[float] = Query(default=None, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db=Depends(get_database),
):
    """搜索服务商"""
    service = ProviderProfileService(db)
    profiles = await service.search_providers(
        skills=skills, min_rating=min_rating, max_hourly_rate=max_hourly_rate, limit=limit
    )
    return [ProviderProfileResponse(**p.model_dump()) for p in profiles]


@router.get("/{user_id}", response_model=ProviderProfileResponse)
async def get_provider_profile_by_id(user_id: int, db=Depends(get_database)):
    """根据用户 ID 获取服务商资料（公开接口）"""
    service = ProviderProfileService(db)
    profile = await service.get_profile(user_id)
    return ProviderProfileResponse(**profile.model_dump())
