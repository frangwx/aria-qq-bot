from enum import IntEnum
from typing import Optional, List, Callable
from functools import wraps

from nonebot.adapters.onebot.v11 import MessageEvent

from .config import get_config
from .logger import get_logger

logger = get_logger()


class PermissionLevel(IntEnum):
    MASTER = 0
    ADMIN = 1
    USER = 2
    BLACKLIST = 3


class PermissionManager:
    def __init__(self):
        self._master_qq: List[str] = []
        self._admins: List[str] = []
        self._blacklist: List[str] = []
        self._load_config()
    
    def _load_config(self):
        master_qq = get_config("bot.master_qq", [])
        admins = get_config("bot.admins", [])
        
        self._master_qq = [str(q) for q in master_qq]
        self._admins = [str(q) for q in admins]
        
        logger.info(f"Loaded permissions: {len(self._master_qq)} masters, {len(self._admins)} admins")
    
    def reload(self):
        self._load_config()
    
    def get_permission_level(self, user_id: str) -> PermissionLevel:
        user_id = str(user_id)
        
        if user_id in self._blacklist:
            return PermissionLevel.BLACKLIST
        
        if user_id in self._master_qq:
            return PermissionLevel.MASTER
        
        if user_id in self._admins:
            return PermissionLevel.ADMIN
        
        return PermissionLevel.USER
    
    def is_master(self, user_id: str) -> bool:
        return self.get_permission_level(user_id) == PermissionLevel.MASTER
    
    def is_admin(self, user_id: str) -> bool:
        level = self.get_permission_level(user_id)
        return level in [PermissionLevel.MASTER, PermissionLevel.ADMIN]
    
    def is_blacklisted(self, user_id: str) -> bool:
        return self.get_permission_level(user_id) == PermissionLevel.BLACKLIST
    
    def add_master(self, user_id: str) -> bool:
        user_id = str(user_id)
        if user_id not in self._master_qq:
            self._master_qq.append(user_id)
            logger.info(f"Added master: {user_id}")
            return True
        return False
    
    def remove_master(self, user_id: str) -> bool:
        user_id = str(user_id)
        if user_id in self._master_qq:
            self._master_qq.remove(user_id)
            logger.info(f"Removed master: {user_id}")
            return True
        return False
    
    def add_admin(self, user_id: str) -> bool:
        user_id = str(user_id)
        if user_id not in self._admins:
            self._admins.append(user_id)
            logger.info(f"Added admin: {user_id}")
            return True
        return False
    
    def remove_admin(self, user_id: str) -> bool:
        user_id = str(user_id)
        if user_id in self._admins:
            self._admins.remove(user_id)
            logger.info(f"Removed admin: {user_id}")
            return True
        return False
    
    def add_to_blacklist(self, user_id: str) -> bool:
        user_id = str(user_id)
        if user_id not in self._blacklist:
            self._blacklist.append(user_id)
            logger.info(f"Added to blacklist: {user_id}")
            return True
        return False
    
    def remove_from_blacklist(self, user_id: str) -> bool:
        user_id = str(user_id)
        if user_id in self._blacklist:
            self._blacklist.remove(user_id)
            logger.info(f"Removed from blacklist: {user_id}")
            return True
        return False
    
    def get_masters(self) -> List[str]:
        return self._master_qq.copy()
    
    def get_admins(self) -> List[str]:
        return self._admins.copy()


permission = PermissionManager()


def require_permission(level: PermissionLevel):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(event: MessageEvent, *args, **kwargs):
            user_id = event.get_user_id()
            user_level = permission.get_permission_level(user_id)
            
            if user_level > level:
                return None
            
            return await func(event, *args, **kwargs)
        return wrapper
    return decorator


def require_master(func: Callable):
    @wraps(func)
    async def wrapper(event: MessageEvent, *args, **kwargs):
        user_id = event.get_user_id()
        if not permission.is_master(user_id):
            await event.finish("权限不足，此命令仅主人可用")
        return await func(event, *args, **kwargs)
    return wrapper


def require_admin(func: Callable):
    @wraps(func)
    async def wrapper(event: MessageEvent, *args, **kwargs):
        user_id = event.get_user_id()
        if not permission.is_admin(user_id):
            await event.finish("权限不足，此命令仅管理员可用")
        return await func(event, *args, **kwargs)
    return wrapper
