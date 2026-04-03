# News 模块测试计划

## 目标
编写测试用例验证 news 模块的 API 请求是否正确，并处理消息格式。

---

## 测试范围

### 1. API 接口测试
- 米游社资讯 API
- 官方网站 HTML 解析


### 2. 消息格式测试
- `format_news_for_push()` 资讯格式化
- `format_hot_topics()` 热点格式化
- `NewsItem.to_dict()` 数据转换

---

## 测试文件结构

```
tests/
├── __init__.py
├── conftest.py          # pytest 配置和 fixtures
├── test_crawler.py      # 爬虫 API 测试
└── test_service.py      # 服务层测试
```

---

## 测试用例

### test_crawler.py

```python
class TestMiyousheAPI:
    """米游社 API 测试"""
    
    async def test_miyoushe_news_api(self):
        """测试资讯 API"""
        url = "https://bbs-api-static.miyoushe.com/painter/wapi/getNewsList"
        params = {"client_type": 4, "gids": 8, "type": 1, "page_size": 5}
        
        response = await client.get(url, params=params)
        data = response.json()
        
        assert data.get("retcode") == 0
        assert len(data.get("data", {}).get("list", [])) > 0

class TestCrawlerIntegration:
    """爬虫集成测试"""
    
    async def test_crawler_fetch_news(self):
        """测试爬虫获取资讯"""
        news_list = await crawler.fetch_miyoushe_news(1, 5)
        
        assert isinstance(news_list, list)
        assert len(news_list) > 0
        assert news_list[0].title != ""
        assert "miyoushe.com" in news_list[0].link
```

### test_service.py

```python
class TestNewsItem:
    """资讯数据模型测试"""
    
    def test_news_item_creation(self):
        """测试资讯创建"""
        news = NewsItem(
            id="test123",
            title="测试标题",
            link="https://example.com/news/1",
            source="miyoushe",
            type="公告"
        )
        
        assert news.id == "test123"
        assert news.title == "测试标题"

class TestNewsServiceFormat:
    """资讯格式化测试"""
    
    def test_format_news_for_push(self):
        """测试资讯格式化"""
        news_list = [NewsItem(...), NewsItem(...)]
        result = service.format_news_for_push(news_list, "测试资讯")
        
        assert "测试资讯" in result
        assert "第一条资讯" in result
    
    def test_format_empty_news(self):
        """测试空资讯处理"""
        result = service.format_news_for_push([], "空资讯")
        assert "暂无" in result
```

---

## 执行命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_crawler.py -v -s

# 显示打印输出
pytest tests/ -v -s
```

---

## 已发现问题与解决方案

### 问题1：米游社 API 返回非标准 JSON
- **现象**: JSON 解析错误
- **解决**: 更换为 painter API

### 问题2：资讯链接无法访问
- **现象**: 生成的链接 404
- **解决**: 更新链接格式为 `https://www.miyoushe.com/zzz/article/{post_id}`

### 问题3：gids 配置错误
- **现象**: 绝区零资讯返回空数据
- **解决**: 绝区零 gids 应为 8

---

## 测试结果

```
tests/test_crawler.py::TestMiyousheAPI::test_miyoushe_webhome_api PASSED
tests/test_crawler.py::TestBilibiliAPI::test_bilibili_hot_api PASSED
tests/test_crawler.py::TestOfficialSite::test_official_news_page PASSED
tests/test_crawler.py::TestCrawlerIntegration::test_crawler_fetch_news PASSED
tests/test_crawler.py::TestCrawlerIntegration::test_crawler_fetch_all PASSED
tests/test_service.py - 7 tests PASSED

============================= 12 passed =============================
```
