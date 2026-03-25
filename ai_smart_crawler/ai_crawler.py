"""
AI智能爬虫系统 - 核心模块
基于研究成果的快速实现

Author: 小罗
Date: 2026-03-25
"""

import asyncio
import json
from typing import Optional, Dict, Any, List, Type, Union
from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrawlStrategy(Enum):
    """爬取策略枚举"""
    STATIC = "static"           # 静态页面 - httpx/bs4
    DYNAMIC = "dynamic"         # JS渲染 - crawl4ai
    BROWSER = "browser"         # 浏览器自动化 - playwright
    API = "api"                 # API调用


@dataclass
class CrawlTask:
    """爬取任务定义"""
    url: str
    instruction: str = ""       # 自然语言指令
    strategy: CrawlStrategy = CrawlStrategy.DYNAMIC
    schema: Optional[Dict] = None  # 结构化提取Schema
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retries: int = 2


@dataclass
class CrawlResult:
    """爬取结果"""
    success: bool
    url: str
    content: str = ""           # 原始内容
    structured_data: Dict = field(default_factory=dict)
    markdown: str = ""          # Markdown格式
    metadata: Dict = field(default_factory=dict)
    error: str = ""
    tokens_used: int = 0


class SmartRouter:
    """智能路由器 - 自动选择最佳爬取策略"""
    
    def __init__(self):
        self.static_extensions = {'.html', '.htm', '.txt', '.xml', '.json'}
        self.dynamic_indicators = [
            'react', 'vue', 'angular', 'spa', 'single-page',
            'javascript', 'ajax', 'xhr'
        ]
    
    async def analyze_url(self, url: str) -> Dict[str, Any]:
        """分析URL特征，判断最佳策略"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # 基础特征
        features = {
            'is_static': any(path.endswith(ext) for ext in self.static_extensions),
            'is_api': path.endswith('.json') or '/api/' in path,
            'domain': parsed.netloc,
        }
        
        # 尝试HEAD请求获取更多信息
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.head(url, timeout=5, follow_redirects=True)
                content_type = response.headers.get('content-type', '')
                features['content_type'] = content_type
                features['is_static'] = features['is_static'] or 'text/html' in content_type
        except Exception:
            pass
        
        return features
    
    async def route(self, task: CrawlTask) -> CrawlStrategy:
        """根据任务特征选择策略"""
        if task.strategy != CrawlStrategy.DYNAMIC:
            return task.strategy
        
        features = await self.analyze_url(task.url)
        
        # 决策逻辑
        if features.get('is_api'):
            return CrawlStrategy.API
        elif features.get('is_static') and not task.instruction:
            return CrawlStrategy.STATIC
        else:
            # 默认使用crawl4ai，它处理大多数情况
            return CrawlStrategy.DYNAMIC


class AICrawler:
    """AI智能爬虫 - 统一入口"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.router = SmartRouter()
        self.openai_api_key = openai_api_key
        self._crawl4ai_available = False
        self._playwright_available = False
        self._init_tools()
    
    def _init_tools(self):
        """初始化工具可用性检查"""
        try:
            import crawl4ai
            self._crawl4ai_available = True
            logger.info("✅ Crawl4AI 已加载")
        except ImportError:
            logger.warning("⚠️ Crawl4AI 未安装，动态爬取功能受限")
        
        try:
            from playwright.async_api import async_playwright
            self._playwright_available = True
            logger.info("✅ Playwright 已加载")
        except ImportError:
            logger.warning("⚠️ Playwright 未安装，浏览器自动化受限")
    
    async def crawl(self, task: CrawlTask) -> CrawlResult:
        """执行爬取任务"""
        # 1. 路由决策
        strategy = await self.router.route(task)
        logger.info(f"🎯 策略选择: {strategy.value} for {task.url}")
        
        # 2. 执行爬取
        try:
            if strategy == CrawlStrategy.STATIC:
                return await self._crawl_static(task)
            elif strategy == CrawlStrategy.DYNAMIC:
                return await self._crawl_dynamic(task)
            elif strategy == CrawlStrategy.BROWSER:
                return await self._crawl_browser(task)
            elif strategy == CrawlStrategy.API:
                return await self._crawl_api(task)
            else:
                return CrawlResult(success=False, url=task.url, error="未知策略")
        except Exception as e:
            logger.error(f"❌ 爬取失败: {e}")
            return CrawlResult(success=False, url=task.url, error=str(e))
    
    async def _crawl_static(self, task: CrawlTask) -> CrawlResult:
        """静态页面爬取 - httpx + BeautifulSoup"""
        import httpx
        from bs4 import BeautifulSoup
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                task.url, 
                headers=task.headers,
                timeout=task.timeout
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取文本内容
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator='\n', strip=True)
            
            return CrawlResult(
                success=True,
                url=task.url,
                content=response.text,
                markdown=text,
                metadata={
                    'title': soup.title.string if soup.title else '',
                    'status_code': response.status_code,
                    'strategy': 'static'
                }
            )
    
    async def _crawl_dynamic(self, task: CrawlTask) -> CrawlResult:
        """动态页面爬取 - Crawl4AI"""
        if not self._crawl4ai_available:
            # 回退到静态爬取
            logger.warning("Crawl4AI不可用，回退到静态爬取")
            return await self._crawl_static(task)
        
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        from crawl4ai.extraction_strategy import LLMExtractionStrategy
        
        config = CrawlerRunConfig(
            cache_mode="BYPASS",
            verbose=False
        )
        
        # 如果有LLM指令，使用LLM提取
        if task.instruction and self.openai_api_key:
            config.extraction_strategy = LLMExtractionStrategy(
                provider="openai/gpt-4o-mini",  # 成本较低的模型
                api_token=self.openai_api_key,
                instruction=task.instruction,
                schema=task.schema,
                extraction_type="schema" if task.schema else "block"
            )
        
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(task.url, config=config)
            
            return CrawlResult(
                success=result.success,
                url=task.url,
                content=result.html if hasattr(result, 'html') else '',
                markdown=result.markdown if hasattr(result, 'markdown') else '',
                structured_data=json.loads(result.extracted_content) if result.extracted_content else {},
                metadata={
                    'strategy': 'dynamic',
                    'links': len(result.links) if hasattr(result, 'links') else 0
                }
            )
    
    async def _crawl_browser(self, task: CrawlTask) -> CrawlResult:
        """浏览器自动化 - Playwright"""
        if not self._playwright_available:
            raise RuntimeError("Playwright未安装")
        
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(task.url, timeout=task.timeout * 1000)
            await page.wait_for_load_state('networkidle')
            
            content = await page.content()
            text = await page.evaluate('() => document.body.innerText')
            
            await browser.close()
            
            return CrawlResult(
                success=True,
                url=task.url,
                content=content,
                markdown=text,
                metadata={'strategy': 'browser'}
            )
    
    async def _crawl_api(self, task: CrawlTask) -> CrawlResult:
        """API调用"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                task.url,
                headers={**task.headers, 'Accept': 'application/json'},
                timeout=task.timeout
            )
            response.raise_for_status()
            
            data = response.json() if 'json' in response.headers.get('content-type', '') else {}
            
            return CrawlResult(
                success=True,
                url=task.url,
                content=response.text,
                structured_data=data,
                markdown=f"```json\n{json.dumps(data, indent=2, ensure_ascii=False)}\n```",
                metadata={'strategy': 'api'}
            )
    
    # ============ 便捷方法 ============
    
    async def quick_fetch(self, url: str) -> str:
        """快速获取页面内容"""
        task = CrawlTask(url=url)
        result = await self.crawl(task)
        return result.markdown if result.success else result.error
    
    async def extract(self, url: str, instruction: str, schema: Optional[Dict] = None) -> Dict:
        """使用LLM提取结构化数据"""
        task = CrawlTask(
            url=url,
            instruction=instruction,
            schema=schema
        )
        result = await self.crawl(task)
        return result.structured_data if result.success else {'error': result.error}
    
    async def batch_crawl(self, urls: List[str], max_concurrent: int = 3) -> List[CrawlResult]:
        """批量爬取"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_limit(url: str) -> CrawlResult:
            async with semaphore:
                return await self.crawl(CrawlTask(url=url))
        
        tasks = [crawl_with_limit(url) for url in urls]
        return await asyncio.gather(*tasks)


# ============ 使用示例 ============

async def demo():
    """演示如何使用AI爬虫"""
    
    # 初始化爬虫 (可选配置OpenAI API Key)
    crawler = AICrawler()
    
    print("=" * 50)
    print("🚀 AI智能爬虫系统演示")
    print("=" * 50)
    
    # 示例1: 快速获取网页内容
    print("\n📄 示例1: 快速获取网页内容")
    url = "https://example.com"
    content = await crawler.quick_fetch(url)
    print(f"URL: {url}")
    print(f"内容长度: {len(content)} 字符")
    print(f"预览: {content[:200]}...")
    
    # 示例2: 结构化数据提取 (需要OpenAI API Key)
    print("\n🔍 示例2: LLM结构化提取")
    print("(需要配置OPENAI_API_KEY环境变量)")
    
    # 示例3: 批量爬取
    print("\n📚 示例3: 批量爬取")
    urls = [
        "https://example.com",
        "https://httpbin.org/json",
    ]
    results = await crawler.batch_crawl(urls)
    for url, result in zip(urls, results):
        status = "✅" if result.success else "❌"
        print(f"{status} {url} - {len(result.markdown)} 字符")
    
    print("\n" + "=" * 50)
    print("✨ 演示完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(demo())
