"""
AI Smart Crawler - 测试套件
"""

import pytest
import asyncio
from ai_smart_crawler import SmartCrawlerSystem, SimpleAICrawler, CrawlTask


class TestSimpleCrawler:
    """测试简化版爬虫"""
    
    @pytest.fixture
    def crawler(self):
        return SimpleAICrawler()
    
    @pytest.mark.asyncio
    async def test_fetch_valid_url(self, crawler):
        """测试正常URL爬取"""
        result = await crawler.crawl(CrawlTask(url="https://httpbin.org/json"))
        assert result.success is True
        assert len(result.content) > 0
        assert 'slideshow' in result.markdown.lower()
    
    @pytest.mark.asyncio
    async def test_fetch_invalid_url(self, crawler):
        """测试无效URL"""
        result = await crawler.crawl(CrawlTask(url="https://invalid-domain-12345.com"))
        assert result.success is False
        assert result.error != ""
    
    @pytest.mark.asyncio
    async def test_batch_crawl(self, crawler):
        """测试批量爬取"""
        urls = [
            "https://httpbin.org/json",
            "https://httpbin.org/html",
        ]
        results = await crawler.batch_crawl(urls, max_concurrent=2)
        assert len(results) == 2
        assert all(r.success for r in results)
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, crawler):
        """测试超时处理"""
        result = await crawler.crawl(CrawlTask(
            url="https://httpbin.org/delay/10",
            timeout=1
        ))
        assert result.success is False


class TestCrawlTask:
    """测试任务类"""
    
    def test_task_creation(self):
        """测试任务创建"""
        task = CrawlTask(
            url="https://example.com",
            timeout=30,
            headers={"User-Agent": "Test"}
        )
        assert task.url == "https://example.com"
        assert task.timeout == 30
        assert task.headers == {"User-Agent": "Test"}


class TestSmartCrawlerSystem:
    """测试系统类"""
    
    @pytest.fixture
    def system(self):
        return SmartCrawlerSystem()
    
    @pytest.mark.asyncio
    async def test_quick_fetch(self, system):
        """测试快速获取"""
        content = await system.quick_fetch("https://httpbin.org/json")
        assert isinstance(content, str)
        assert len(content) > 0
    
    @pytest.mark.asyncio
    async def test_batch_crawl_system(self, system):
        """测试系统批量爬取"""
        urls = ["https://httpbin.org/json", "https://httpbin.org/html"]
        results = await system.batch_crawl(urls)
        assert len(results) == 2
        assert all(hasattr(r, 'success') for r in results)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
