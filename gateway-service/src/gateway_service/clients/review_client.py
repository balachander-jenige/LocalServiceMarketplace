from typing import Any, Dict, List

from ..core.config import settings
from .base_client import BaseClient


class ReviewClient(BaseClient):
    def __init__(self):
        super().__init__(settings.REVIEW_SERVICE_URL)

    async def create_review(self, token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建评价"""
        return await self._make_request("POST", "/reviews/", token=token, json_data=data)

    async def get_provider_rating(self, provider_id: int) -> Dict[str, Any]:
        """获取服务商评分"""
        return await self._make_request("GET", f"/reviews/provider/{provider_id}/rating")

    async def get_provider_reviews(self, provider_id: int) -> List[Dict[str, Any]]:
        """获取服务商评价列表"""
        return await self._make_request("GET", f"/reviews/provider/{provider_id}")

    async def get_my_provider_rating(self, token: str) -> Dict[str, Any]:
        """获取当前 Provider 自己的评分"""
        return await self._make_request("GET", "/reviews/provider/me/rating", token=token)

    async def get_my_provider_reviews(self, token: str) -> List[Dict[str, Any]]:
        """获取当前 Provider 自己的评价列表"""
        return await self._make_request("GET", "/reviews/provider/me/reviews", token=token)


review_client = ReviewClient()
