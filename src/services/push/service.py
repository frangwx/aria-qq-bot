from typing import List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.services.news import news_service, NewsItem
from src.utils import get_config, get_logger

logger = get_logger()

scheduler = AsyncIOScheduler()


class PushService:
    def __init__(self):
        self.bot = None
        self.morning_enabled = get_config("push.morning.enabled", True)
        self.morning_time = get_config("push.morning.time", "08:00")
        self.morning_targets = get_config("push.morning.targets", [])
        
        self.evening_enabled = get_config("push.evening.enabled", True)
        self.evening_time = get_config("push.evening.time", "20:00")
        self.evening_targets = get_config("push.evening.targets", [])
    
    def set_bot(self, bot):
        self.bot = bot
    
    async def push_to_targets(self, message: str, targets: List[str]):
        if not self.bot:
            logger.warning("Bot not set, cannot push message")
            return
        
        for target in targets:
            try:
                if target.startswith("group_"):
                    group_id = target.replace("group_", "")
                    await self.bot.call_api(
                        "send_group_msg",
                        group_id=int(group_id),
                        message=message
                    )
                else:
                    user_id = target.replace("user_", "")
                    await self.bot.call_api(
                        "send_private_msg",
                        user_id=int(user_id),
                        message=message
                    )
                logger.info(f"Pushed message to {target}")
            except Exception as e:
                logger.error(f"Failed to push to {target}: {e}")
    
    async def morning_push(self):
        logger.info("Starting morning news push")
        
        news_list = await news_service.fetch_latest_news(24)
        await news_service.save_news(news_list)
        
        unpushed = await news_service.get_unpushed_news()
        
        if unpushed:
            message = news_service.format_news_for_push(unpushed, "早间资讯")
            await self.push_to_targets(message, self.morning_targets)
            
            await news_service.mark_pushed([n.id for n in unpushed])
    
    async def evening_push(self):
        logger.info("Starting evening hot topics push")
        
        news_list = await news_service.fetch_latest_news(12)
        await news_service.save_news(news_list)
        
        if news_list:
            message = news_service.format_news_for_push(news_list[:10], "今日热点")
            await self.push_to_targets(message, self.evening_targets)
    
    def setup_scheduled_tasks(self):
        if self.morning_enabled and self.morning_targets:
            hour, minute = map(int, self.morning_time.split(":"))
            scheduler.add_job(
                self.morning_push,
                CronTrigger(hour=hour, minute=minute),
                id="morning_push",
                replace_existing=True
            )
            logger.info(f"Scheduled morning push at {self.morning_time}")
        
        if self.evening_enabled and self.evening_targets:
            hour, minute = map(int, self.evening_time.split(":"))
            scheduler.add_job(
                self.evening_push,
                CronTrigger(hour=hour, minute=minute),
                id="evening_push",
                replace_existing=True
            )
            logger.info(f"Scheduled evening push at {self.evening_time}")
    
    def start(self):
        self.setup_scheduled_tasks()
        scheduler.start()
        logger.info("Push service started")
    
    def stop(self):
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Push service stopped")


push_service = PushService()
