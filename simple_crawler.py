#!/usr/bin/env python3
"""
AI爬虫系统 - 简化版 (仅使用httpx+bs4)
无需额外安装即可运行
"""

import asyncio
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from urllib.parse import urlparse

@dataclass
class CrawlTask:
    """爬取任务"""
    url: str
    instruction: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30

@dataclass
class CrawlResult:
    """爬取结果"""
    success: bool
    url: str
    content: str = ""
    markdown: str = ""
    structured_data: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    error: str = ""


class SimpleAICrawler:
    """简化版AI爬虫 - 使用httpx+bs4"""
    
    def __init__(self):
        self.session = None
    
    async def crawl(self, task: CrawlTask) -> CrawlResult:
        """执行爬取"""
        try:
            import httpx
            from bs4 import BeautifulSoup
            
            async with httpx.AsyncClient() as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                headers.update(task.headers)
                
                response = await client.get(
                    task.url,
                    headers=headers,
                    timeout=task.timeout,
                    follow_redirects=True
                )
                response.raise_for_status()
                
                # 解析内容
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 移除脚本和样式
                for tag in soup(['script', 'style', 'nav', 'footer']):
                    tag.decompose()
                
                # 提取标题
                title = soup.title.string if soup.title else ''
                
                # 提取正文
                text = soup.get_text(separator='\n', strip=True)
                
                # 生成Markdown
                markdown = f"# {title}\n\n{text}" if title else text
                
                # 限制内容长度，防止超大页面
                max_length = 10000
                if len(markdown) > max_length:
                    markdown = markdown[:max_length] + "\n\n[内容已截断...]"
                
                return CrawlResult(
                    success=True,
                    url=task.url,
                    content=response.text,
                    markdown=markdown[:5000],  # 限制长度
                    metadata={
                        'title': title,
                        'status_code': response.status_code,
                        'content_type': response.headers.get('content-type', '')
                    }
                )
                
        except Exception as e:
            return CrawlResult(
                success=False,
                url=task.url,
                error=str(e)
            )
    
    async def quick_fetch(self, url: str) -> str:
        """快速获取"""
        result = await self.crawl(CrawlTask(url=url))
        return result.markdown if result.success else result.error
    
    async def batch_crawl(self, urls: List[str], max_concurrent: int = 3) -> List[CrawlResult]:
        """批量爬取"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_limited(url):
            async with semaphore:
                return await self.crawl(CrawlTask(url=url))
        
        tasks = [crawl_limited(url) for url in urls]
        return await asyncio.gather(*tasks)


class SmartCrawlerSystem:
    """简化版智能爬虫系统"""
    
    def __init__(self):
        self.crawler = SimpleAICrawler()
        print("✅ 简化版AI爬虫系统已初始化")
        print("   (使用httpx + BeautifulSoup4)")
    
    async def quick_fetch(self, url: str) -> str:
        return await self.crawler.quick_fetch(url)
    
    async def batch_crawl(self, urls: List[str]) -> List[CrawlResult]:
        return await self.crawler.batch_crawl(urls)
    
    async def demo(self):
        """运行演示"""
        print("\n" + "=" * 50)
        print("🚀 AI爬虫系统演示 (简化版)")
        print("=" * 50)
        
        # 测试1: 简单爬取
        print("\n📄 测试1: 爬取示例页面")
        print("-" * 40)
        try:
            content = await self.quick_fetch("https://httpbin.org/json")
            print(f"✅ 成功!")
            print(f"内容:\n{content[:300]}...")
        except Exception as e:
            print(f"❌ 失败: {e}")
        
        # 测试2: 批量爬取
        print("\n📚 测试2: 批量爬取")
        print("-" * 40)
        try:
            urls = [
                "https://httpbin.org/json",
                "https://example.com",
            ]
            results = await self.batch_crawl(urls)
            for url, result in zip(urls, results):
                status = "✅" if result.success else "❌"
                size = len(result.markdown) if result.success else 0
                print(f"{status} {url} ({size} chars)")
        except Exception as e:
            print(f"❌ 批量爬取失败: {e}")
        
        print("\n" + "=" * 50)
        print("✨ 演示完成!")
        print("=" * 50)


# ============ 主入口 ============

if __name__ == "__main__":
    system = SmartCrawlerSystem()
    asyncio.run(system.demo())
