import asyncpg
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ...config import Config
from ...logger import LOGGER

class AdminManager:
    def __init__(self):
        self.pool = None
        self._init_db()
        
    async def _init_db(self):
        """Initialize database tables"""
        self.pool = await asyncpg.create_pool(Config.DATABASE_URL)
        
        async with self.pool.acquire() as conn:
            # Admin table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    user_id BIGINT PRIMARY KEY,
                    permissions TEXT[],
                    added_at TIMESTAMP NOT NULL,
                    added_by BIGINT,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Admin logs table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS admin_logs (
                    id SERIAL PRIMARY KEY,
                    admin_id BIGINT NOT NULL,
                    action TEXT NOT NULL,
                    details JSONB,
                    status TEXT DEFAULT 'success',
                    timestamp TIMESTAMP NOT NULL
                )
            ''')
            
            # User bans table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_bans (
                    user_id BIGINT PRIMARY KEY,
                    banned_by BIGINT NOT NULL,
                    reason TEXT,
                    banned_at TIMESTAMP NOT NULL
                )
            ''')

    async def add_admin(
        self,
        user_id: int,
        permissions: List[str],
        added_by: int
    ) -> bool:
        """Add new admin"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO admins (user_id, permissions, added_at, added_by)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET permissions = $2, is_active = TRUE
                ''', user_id, permissions, datetime.utcnow(), added_by)
                
                await self.log_action(
                    added_by,
                    'add_admin',
                    {'target_user': user_id, 'permissions': permissions}
                )
                return True
        except Exception as e:
            LOGGER.error(f"Failed to add admin: {str(e)}")
            return False

    async def remove_admin(self, user_id: int, removed_by: int) -> bool:
        """Remove admin"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    UPDATE admins SET is_active = FALSE 
                    WHERE user_id = $1
                ''', user_id)
                
                await self.log_action(
                    removed_by,
                    'remove_admin',
                    {'target_user': user_id}
                )
                return True
        except Exception as e:
            LOGGER.error(f"Failed to remove admin: {str(e)}")
            return False

    async def get_admin_permissions(self, user_id: int) -> List[str]:
        """Get admin permissions"""
        async with self.pool.acquire() as conn:
            record = await conn.fetchrow('''
                SELECT permissions FROM admins 
                WHERE user_id = $1 AND is_active = TRUE
            ''', user_id)
            return record['permissions'] if record else []

    async def log_action(
        self,
        admin_id: int,
        action: str,
        details: dict,
        status: str = 'success'
    ):
        """Log admin action"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO admin_logs 
                    (admin_id, action, details, status, timestamp)
                    VALUES ($1, $2, $3, $4, $5)
                ''', admin_id, action, details, status, datetime.utcnow())
        except Exception as e:
            LOGGER.error(f"Failed to log admin action: {str(e)}")

    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        async with self.pool.acquire() as conn:
            records = await conn.fetch('SELECT * FROM users')
            return [dict(r) for r in records]

    async def get_active_users_count(self) -> int:
        """Get count of active users today"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval('''
                SELECT COUNT(*) FROM users 
                WHERE last_active >= $1
            ''', datetime.utcnow() - timedelta(days=1))

    async def get_banned_users_count(self) -> int:
        """Get count of banned users"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval('SELECT COUNT(*) FROM user_bans')
