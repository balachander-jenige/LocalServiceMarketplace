import json
from aio_pika import IncomingMessage
from ...core.mongodb import get_database
from ...dao.customer_profile_dao import CustomerProfileDAO
from ...dao.provider_profile_dao import ProviderProfileDAO
from ...models.customer_profile import CustomerProfile, LocationEnum
from ...models.provider_profile import ProviderProfile

async def handle_user_registered(message: IncomingMessage):
    """
    处理用户注册事件，自动创建对应的 Profile
    Handle user registration event, automatically create corresponding profile
    """
    async with message.process():
        data = json.loads(message.body.decode())
        user_id = data.get("user_id")
        role_id = data.get("role_id")
        
        db = get_database()
        
        # role_id: 1=customer, 2=provider, 3=admin
        if role_id == 1:
            # 创建客户资料
            customer_dao = CustomerProfileDAO(db)
            existing = await customer_dao.get_by_user_id(user_id)
            
            if not existing:
                profile = CustomerProfile(
                    user_id=user_id,
                    location=LocationEnum.NORTH,
                    address=None,
                    budget_preference=0.0
                    # balance 字段已删除 - 第三阶段修改
                )
                await customer_dao.create(profile)
                print(f"✅ Created customer profile for user {user_id}")
        
        elif role_id == 2:
            # 创建服务商资料
            provider_dao = ProviderProfileDAO(db)
            existing = await provider_dao.get_by_user_id(user_id)
            
            if not existing:
                profile = ProviderProfile(
                    user_id=user_id,
                    skills=[],
                    experience_years=0,
                    hourly_rate=0.0,
                    availability=None,
                    portfolio=[],
                    # total_earnings 字段已删除 - 第三阶段修改
                    rating=5.0,
                    total_reviews=0
                )
                await provider_dao.create(profile)
                print(f"✅ Created provider profile for user {user_id}")