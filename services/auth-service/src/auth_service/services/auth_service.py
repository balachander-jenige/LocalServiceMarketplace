from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import create_access_token, hash_password, verify_password
from ..dao.role_dao import RoleDAO
from ..dao.user_dao import UserDAO
from ..domain.events.user_registered import UserRegisteredEvent
from ..events.publishers.event_publisher import EventPublisher


class AuthService:
    """Authentication Service"""

    @staticmethod
    async def register(db: AsyncSession, username: str, email: str, password: str, role_id: int):
        """User Registration"""
        # Hash Password
        password_hash = hash_password(password)

        # Create User
        user = await UserDAO.create_user(db, username, email, password_hash, role_id)

        # Publish User Registered Event
        event = UserRegisteredEvent(
            user_id=user.id, username=user.username, email=user.email, role_id=user.role_id, timestamp=datetime.now(UTC)
        )
        await EventPublisher.publish_user_registered(event)

        return user

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str):
        """User Login"""
        user = await UserDAO.get_user_by_email(db, email)

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        # Generate Token containing user_id and role_id
        token_data = {"sub": str(user.id), "role": user.role_id}  # Add role information
        token = create_access_token(token_data)
        return token
