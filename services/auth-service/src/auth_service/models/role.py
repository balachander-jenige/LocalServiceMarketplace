from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    # Relationships
    users = relationship("User", back_populates="role")
