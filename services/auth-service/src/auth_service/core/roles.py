"""RoleConstant Definitions"""


class RoleConstants:
    """Role ID Constants"""

    CUSTOMER = 1
    PROVIDER = 2
    ADMIN = 3

    @staticmethod
    def get_role_name(role_id: int) -> str:
        """ByRole ID GetRoleName称"""
        role_names = {1: "customer", 2: "provider", 3: "admin"}
        return role_names.get(role_id, "unknown")

    @staticmethod
    def is_valid_role(role_id: int) -> bool:
        """VerifyRole ID Is Valid"""
        return role_id in [1, 2, 3]
