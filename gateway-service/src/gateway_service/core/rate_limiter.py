from fastapi import HTTPException, Request, status
from datetime import datetime, timedelta
from collections import defaultdict
from .config import settings

class RateLimiter:
    def __init__(self):
        # 存储每个 IP 的请求时间戳
        self.requests = defaultdict(list)
    
    async def check_rate_limit(self, request: Request):
        """检查请求是否超过限流阈值"""
        client_ip = request.client.host
        now = datetime.now()
        
        # 清理超过1分钟的旧记录
        cutoff_time = now - timedelta(minutes=1)
        self.requests[client_ip] = [
            timestamp for timestamp in self.requests[client_ip]
            if timestamp > cutoff_time
        ]
        
        # 检查是否超过限制
        if len(self.requests[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # 记录当前请求
        self.requests[client_ip].append(now)

rate_limiter = RateLimiter()