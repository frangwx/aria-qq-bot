from typing import List, Dict

from .crawler import crawler, NewsItem, HotTopic
from src.storage import db
from src.utils import get_logger

logger = get_logger()


class NewsService:
    def __init__(self):
        self.crawler = crawler
    
    async def fetch_latest_news(self, hours: int = 24) -> List[NewsItem]:
        news_list = await self.crawler.fetch_all_news()
        
        current_time = int(__import__('time').time())
        time_threshold = current_time - (hours * 3600)
        
        recent_news = [
            n for n in news_list
            if n.publish_time > time_threshold or n.publish_time == 0
        ]
        
        return recent_news
    
    async def get_news_by_type(self, news_type: str) -> List[NewsItem]:
        news_list = await self.crawler.fetch_all_news()
        return [n for n in news_list if n.type == news_type]
    
    async def save_news(self, news_list: List[NewsItem]):
        news_dicts = [n.to_dict() for n in news_list]
        await db.save_news(news_dicts)
        logger.info(f"Saved {len(news_list)} news to database")
    
    async def get_unpushed_news(self) -> List[NewsItem]:
        news_records = await db.get_unpushed_news()
        return [
            NewsItem(
                id=n.id,
                title=n.title,
                link=n.link,
                source=n.source,
                type=n.type,
                content=n.content or "",
                publish_time=n.publish_time or 0,
                cover=n.cover
            )
            for n in news_records
        ]
    
    async def mark_pushed(self, news_ids: List[str]):
        await db.mark_news_pushed(news_ids)
    
    def format_news_for_push(self, news_list: List[NewsItem], title: str = "资讯") -> str:
        if not news_list:
            return f"暂无{title}"
        
        lines = [f"【{title}】", f"📅 日期：{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}", ""]
        
        for i, news in enumerate(news_list[:10], 1):
            lines.append(f"{i}. [{news.type}] {news.title}")
            lines.append(f"   🔗 {news.link}")
        
        return "\n".join(lines)
    
    async def fetch_hot_topics(self) -> List[HotTopic]:
        return await self.crawler.fetch_all_hot_topics()
    
    def format_hot_topics(self, hot_list: List[HotTopic], title: str = "热点话题") -> str:
        if not hot_list:
            return f"暂无{title}"
        
        lines = [f"【{title}】", f"📅 日期：{__import__('datetime').datetime.now().strftime('%Y-%m-%d')}", ""]
        
        for i, hot in enumerate(hot_list[:10], 1):
            source_icon = "📺" if hot.source == "bilibili" else "🎮"
            hot_str = self._format_hot_value(hot.hot_value)
            lines.append(f"{i}. {source_icon} {hot.title}")
            lines.append(f"   🔥 {hot_str} | 👤 {hot.author or '未知'}")
            lines.append(f"   🔗 {hot.link}")
        
        return "\n".join(lines)
    
    def _format_hot_value(self, value: int) -> str:
        if value >= 10000:
            return f"{value / 10000:.1f}万"
        return str(value)


news_service = NewsService()
