import redis
from etc.env_settings import Setting
from aioredlock import Aioredlock, LockError, Sentinel

class RedisConnection():
    __instance = None
    __redis_instances = [{
        'host': Setting.REDIS_HOST.value,
        'port': Setting.REDIS_PORT.value,
        'db': int(Setting.REDIS_DB.value),  
    },]
    redis = None
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.redis = redis.Redis(Setting.REDIS_HOST.value, Setting.REDIS_PORT.value, Setting.REDIS_DB.value)
            print(f"\n\nRedis connection established: {cls.redis.ping()}\n\n")
            cls.__lock_manager = Aioredlock(cls.__redis_instances)
            print(f"\n\nRedis lock manager established: {cls.__lock_manager}\n\n")
            
        return cls.__instance
    
    @classmethod
    async def is_lock_free(cls, lock_name): # WORKS
        return not await cls.__lock_manager.is_locked("resource_name")
    
    @classmethod
    async def acquire_lock_and_run(cls, lock_name:str, func, args=None, is_async=False):
        try:
            async with await cls.__lock_manager.lock(lock_name) as lock:
                assert lock.valid is True 
                
                if is_async == False:
                    if args is None:
                        result = func()
                    else:
                        result = func(args)
                if is_async == True:
                    if args is None:
                        result = await func()
                    else:
                        result = await func(args)
                
                # await lock.extend()
                # do more stuff here...
            assert lock.valid is False
            return result
        except LockError:
            print("Lock not acquired.")
            return False
        
    @classmethod
    async def shutdown(cls):
        await cls.__lock_manager.destroy()
    
    