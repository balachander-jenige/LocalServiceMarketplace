"""角色常量定义"""

class RoleConstants:
    """角色 ID 常量"""
    CUSTOMER = 1
    PROVIDER = 2
    ADMIN = 3
    
    @staticmethod
    def get_role_name(role_id: int) -> str:
        """根据角色 ID 获取角色名称"""
        role_names = {
            1: "customer",
            2: "provider",
            3: "admin"
        }
        return role_names.get(role_id, "unknown")
    
    @staticmethod
    def is_valid_role(role_id: int) -> bool:
        """验证角色 ID 是否有效"""
        return role_id in [1, 2, 3]
