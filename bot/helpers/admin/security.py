from typing import Optional, List
import jwt
from datetime import datetime, timedelta
from ...config import Config
from ...logger import LOGGER

class AdminSecurity:
    def __init__(self):
        self.secret = Config.ADMIN_SETTINGS['SECURITY']['SECRET_KEY']
        self.algorithm = Config.ADMIN_SETTINGS['SECURITY']['ALGORITHM']
        self.session_timeout = Config.ADMIN_SETTINGS['SECURITY']['SESSION_TIMEOUT']

    async def generate_admin_token(
        self,
        user_id: int,
        permissions: List[str]
    ) -> str:
        """Generate admin session token"""
        try:
            payload = {
                'user_id': user_id,
                'permissions': permissions,
                'exp': datetime.utcnow() + timedelta(seconds=self.session_timeout)
            }
            return jwt.encode(payload, self.secret, algorithm=self.algorithm)
        except Exception as e:
            LOGGER.error(f"Failed to generate admin token: {str(e)}")
            raise

    async def verify_admin_token(self, token: str) -> Optional[dict]:
        """Verify admin token"""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError(lang.s.ADMIN_SESSION_EXPIRED)
        except jwt.InvalidTokenError:
            raise ValueError(lang.s.ADMIN_INVALID_TOKEN)

    async def check_permission(
        self,
        user_id: int,
        required_permission: str
    ) -> bool:
        """Check if admin has required permission"""
        try:
            admin_db = AdminManager()
            permissions = await admin_db.get_admin_permissions(user_id)
            return required_permission in permissions or 'super_admin' in permissions
        except Exception as e:
            LOGGER.error(f"Permission check failed: {str(e)}")
            return False

    async def verify_2fa(self, user_id: int, code: str) -> bool:
        """Verify 2FA code if enabled"""
        if not Config.ADMIN_SETTINGS['SECURITY']['REQUIRE_2FA']:
            return True
            
        try:
            # Implement your 2FA verification logic here
            return True
        except Exception as e:
            LOGGER.error(f"2FA verification failed: {str(e)}")
            return False
