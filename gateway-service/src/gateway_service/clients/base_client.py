from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status


class BaseClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = 10.0

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        token: Optional[str] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Common HTTP 请求Method"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=json_data)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json=json_data)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Check响应Status
                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.json().get("detail", "Service request failed")
                    )

                return response.json()

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Service unavailable: {str(e)}"
            )
