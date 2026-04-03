import hashlib
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from src.utils import get_config, get_logger

logger = get_logger()


@dataclass
class NewsItem:
    id: str
    title: str
    link: str
    source: str
    type: str
    content: str
    publish_time: int
    cover: Optional[str] = None
    created_at: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = int(datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "link": self.link,
            "source": self.source,
            "type": self.type,
            "content": self.content,
            "publish_time": self.publish_time,
            "cover": self.cover,
            "created_at": self.created_at
        }


@dataclass
class HotTopic:
    id: str
    title: str
    link: str
    source: str
    hot_value: int
    cover: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = int(datetime.now().timestamp())


class NewsCrawler:
    MIYOUSHE_GIDS = 8
    
    def __init__(self):
        self.request_interval = get_config("crawler.request_interval", 2.0)
        self.max_retries = get_config("crawler.max_retries", 3)
        self.user_agents = get_config("crawler.user_agents", [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ])
    
    def _get_headers(self, referer: str = "https://bbs.mihoyo.com/") -> Dict[str, str]:
        return {
            "Referer": referer,
            "User-Agent": random.choice(self.user_agents),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://bbs.mihoyo.com",
        }
    
    def _generate_id(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()[:16]
    
    async def fetch_miyoushe_news(
        self,
        news_type: int = 1,
        page_size: int = 20
    ) -> List[NewsItem]:
        url = "https://bbs-api-static.miyoushe.com/painter/wapi/getNewsList"
        params = {
            "client_type": 4,
            "gids": self.MIYOUSHE_GIDS,
            "page_size": page_size,
            "type": news_type
        }
        
        type_names = {1: "公告", 2: "活动", 3: "资讯"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                
                text = response.text
                if not text:
                    logger.warning("MiyoUShe API returned empty response")
                    return []
                
                try:
                    data = response.json()
                except Exception as json_err:
                    logger.error(f"MiyoUShe API JSON parse error: {json_err}, response[:200]: {text[:200]}")
                    return []
                
                if data.get("retcode") != 0:
                    logger.error(f"MiyoUShe API error: {data.get('message')}")
                    return []
                
                news_list = []
                for item in data.get("data", {}).get("list", []):
                    post = item.get("post", {})
                    news = NewsItem(
                        id=post.get("post_id", self._generate_id(post.get("subject", ""))),
                        title=post.get("subject", ""),
                        link=f"https://www.miyoushe.com/zzz/article/{post.get('post_id')}",
                        source="miyoushe",
                        type=type_names.get(news_type, "资讯"),
                        content=post.get("content", "")[:200] if post.get("content") else "",
                        publish_time=post.get("created_at", 0),
                        cover=post.get("cover")
                    )
                    news_list.append(news)
                
                logger.info(f"Fetched {len(news_list)} news from MiyoUShe (type={news_type})")
                return news_list
                
        except Exception as e:
            logger.error(f"Failed to fetch MiyoUShe news: {e}")
            return []
    
    async def fetch_official_news(self) -> List[NewsItem]:
        url = "https://zenless.hoyoverse.com/zh-cn/news"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self._get_headers("https://zenless.hoyoverse.com/"),
                    timeout=30.0
                )
                soup = BeautifulSoup(response.text, 'lxml')
                
                news_list = []
                for item in soup.select('.news-list-item'):
                    try:
                        title_elem = item.select_one('.news-list-item-title')
                        link_elem = item.select_one('a')
                        category_elem = item.select_one('.news-list-item-type')
                        
                        if not title_elem or not link_elem:
                            continue
                        
                        link = link_elem.get('href', '')
                        if not link.startswith('http'):
                            link = f"https://zenless.hoyoverse.com{link}"
                        
                        news = NewsItem(
                            id=self._generate_id(link),
                            title=title_elem.text.strip(),
                            link=link,
                            source="official",
                            type=category_elem.text.strip() if category_elem else "资讯",
                            content="",
                            publish_time=0
                        )
                        news_list.append(news)
                    except Exception as e:
                        logger.warning(f"Failed to parse news item: {e}")
                        continue
                
                if not news_list:
                    for item in soup.select('a[href*="/news/"]'):
                        try:
                            title = item.get_text(strip=True)
                            link = item.get('href', '')
                            if title and link:
                                if not link.startswith('http'):
                                    link = f"https://zenless.hoyoverse.com{link}"
                                news = NewsItem(
                                    id=self._generate_id(link),
                                    title=title,
                                    link=link,
                                    source="official",
                                    type="资讯",
                                    content="",
                                    publish_time=0
                                )
                                news_list.append(news)
                        except Exception:
                            continue
                
                logger.info(f"Fetched {len(news_list)} news from official site")
                return news_list
                
        except Exception as e:
            logger.error(f"Failed to fetch official news: {e}")
            return []
    
    async def fetch_miyoushe_hot(self, page_size: int = 10) -> List[HotTopic]:
        url = "https://bbs-api-static.miyoushe.com/apihub/wapi/webHome"
        params = {
            "gids": self.MIYOUSHE_GIDS
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=30.0
                )
                
                text = response.text
                if not text:
                    return []
                
                try:
                    data = response.json()
                except Exception:
                    logger.error(f"MiyoUShe Hot API JSON parse error, response[:200]: {text[:200]}")
                    return []
                
                if data.get("retcode") != 0:
                    logger.error(f"MiyoUShe Hot API error: {data.get('message')}")
                    return []
                
                hot_list = []
                for item in data.get("data", {}).get("recommended_posts", [])[:page_size]:
                    post = item.get("post", {})
                    hot = HotTopic(
                        id=post.get("post_id", self._generate_id(post.get("subject", ""))),
                        title=post.get("subject", ""),
                        link=f"https://www.miyoushe.com/zzz/article/{post.get('post_id')}",
                        source="miyoushe",
                        hot_value=post.get("stat", {}).get("view", 0),
                        cover=post.get("cover"),
                        author=post.get("user", {}).get("nickname")
                    )
                    hot_list.append(hot)
                
                logger.info(f"Fetched {len(hot_list)} hot topics from MiyoUShe")
                return hot_list
                
        except Exception as e:
            logger.error(f"Failed to fetch MiyoUShe hot: {e}")
            return []
    
    async def fetch_bilibili_hot(self, page_size: int = 10) -> List[HotTopic]:
        url = "https://api.bilibili.com/x/web-interface/popular/series/one"
        params = {
            "number": 1,
            "ps": page_size
        }
        
        headers = {
            "Referer": "https://www.bilibili.com/",
            "User-Agent": random.choice(self.user_agents)
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=30.0
                )
                data = response.json()
                
                if data.get("code") != 0:
                    logger.error(f"Bilibili Hot API error: {data.get('message')}")
                    return []
                
                hot_list = []
                archives = data.get("data", {}).get("archives", [])
                
                for item in archives[:page_size]:
                    title = item.get("title", "")
                    if "绝区零" not in title and "ZZZ" not in title.upper():
                        continue
                    
                    hot = HotTopic(
                        id=str(item.get("aid", "")),
                        title=title,
                        link=f"https://www.bilibili.com/video/{item.get('bvid')}",
                        source="bilibili",
                        hot_value=item.get("stat", {}).get("view", 0),
                        cover=item.get("pic"),
                        author=item.get("owner", {}).get("name")
                    )
                    hot_list.append(hot)
                
                logger.info(f"Fetched {len(hot_list)} hot topics from Bilibili")
                return hot_list
                
        except Exception as e:
            logger.error(f"Failed to fetch Bilibili hot: {e}")
            return []
    
    async def fetch_all_news(self) -> List[NewsItem]:
        news_list = []
        
        announcements = await self.fetch_miyoushe_news(news_type=1, page_size=10)
        news_list.extend(announcements)
        
        activities = await self.fetch_miyoushe_news(news_type=2, page_size=10)
        news_list.extend(activities)
        
        info = await self.fetch_miyoushe_news(news_type=3, page_size=10)
        news_list.extend(info)
        
        official_news = await self.fetch_official_news()
        news_list.extend(official_news)
        
        seen_ids = set()
        unique_news = []
        for news in news_list:
            if news.id not in seen_ids:
                seen_ids.add(news.id)
                unique_news.append(news)
        
        unique_news.sort(key=lambda x: x.publish_time, reverse=True)
        
        return unique_news
    
    async def fetch_all_hot_topics(self) -> List[HotTopic]:
        hot_list = []
        
        miyoushe_hot = await self.fetch_miyoushe_hot(10)
        hot_list.extend(miyoushe_hot)
        
        bilibili_hot = await self.fetch_bilibili_hot(10)
        hot_list.extend(bilibili_hot)
        
        hot_list.sort(key=lambda x: x.hot_value, reverse=True)
        
        return hot_list[:20]


crawler = NewsCrawler()
