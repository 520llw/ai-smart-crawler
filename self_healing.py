"""
自修复模块 - 自动诊断和修复爬取失败
"""

import asyncio
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time


class FailureType(Enum):
    """失败类型"""
    NETWORK = "network"           # 网络错误
    TIMEOUT = "timeout"           # 超时
    PARSE_ERROR = "parse_error"   # 解析错误
    BLOCKED = "blocked"           # 被反爬
    NOT_FOUND = "not_found"       # 404
    UNKNOWN = "unknown"           # 未知错误


@dataclass
class FailureRecord:
    """失败记录"""
    url: str
    error: str
    failure_type: FailureType
    timestamp: float
    retry_count: int = 0
    fix_applied: Optional[str] = None


class SelfHealingCrawler:
    """自修复爬虫 - 自动处理失败"""
    
    def __init__(self, base_crawler):
        self.crawler = base_crawler
        self.failure_history: List[FailureRecord] = []
        self.max_retries = 3
        
        # 修复策略注册表
        self.fix_strategies: Dict[FailureType, List[Callable]] = {
            FailureType.NETWORK: [
                self._fix_add_delay,
                self._fix_change_headers,
            ],
            FailureType.TIMEOUT: [
                self._fix_increase_timeout,
                self._fix_use_browser,
            ],
            FailureType.BLOCKED: [
                self._fix_use_browser,
                self._fix_change_headers,
                self._fix_add_proxy,
            ],
            FailureType.PARSE_ERROR: [
                self._fix_use_browser,
                self._fix_retry_with_fallback,
            ],
        }
    
    async def crawl_with_healing(self, task) -> Dict:
        """带自修复的爬取"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                result = await self.crawler.crawl(task)
                
                if result.success:
                    return {
                        "success": True,
                        "result": result,
                        "retries": attempt,
                        "healing_applied": attempt > 0
                    }
                else:
                    raise Exception(result.error)
                    
            except Exception as e:
                last_error = str(e)
                failure_type = self._classify_error(last_error)
                
                print(f"⚠️ 尝试 {attempt + 1}/{self.max_retries} 失败: {failure_type.value}")
                
                # 记录失败
                record = FailureRecord(
                    url=task.url,
                    error=last_error,
                    failure_type=failure_type,
                    timestamp=time.time(),
                    retry_count=attempt
                )
                self.failure_history.append(record)
                
                # 尝试修复
                if attempt < self.max_retries - 1:
                    fixed_task = await self._attempt_fix(task, failure_type, attempt)
                    if fixed_task:
                        task = fixed_task
                        record.fix_applied = f"strategy_{attempt}"
                        print(f"🔧 应用修复策略: {record.fix_applied}")
                    else:
                        print("❌ 无可用修复策略")
                        break
        
        # 所有重试失败
        return {
            "success": False,
            "error": last_error,
            "retries": self.max_retries,
            "failure_type": failure_type.value,
            "suggestion": self._get_suggestion(failure_type)
        }
    
    def _classify_error(self, error: str) -> FailureType:
        """分类错误类型"""
        error_lower = error.lower()
        
        if any(k in error_lower for k in ['timeout', 'timed out']):
            return FailureType.TIMEOUT
        elif any(k in error_lower for k in ['connection', 'network', 'dns']):
            return FailureType.NETWORK
        elif any(k in error_lower for k in ['403', 'blocked', 'forbidden', 'captcha']):
            return FailureType.BLOCKED
        elif any(k in error_lower for k in ['404', 'not found']):
            return FailureType.NOT_FOUND
        elif any(k in error_lower for k in ['parse', 'json', 'extract']):
            return FailureType.PARSE_ERROR
        else:
            return FailureType.UNKNOWN
    
    async def _attempt_fix(self, task, failure_type: FailureType, attempt: int):
        """尝试修复"""
        strategies = self.fix_strategies.get(failure_type, [])
        
        if attempt < len(strategies):
            fix_func = strategies[attempt]
            return await fix_func(task)
        
        return None
    
    # ============ 修复策略 ============
    
    async def _fix_add_delay(self, task):
        """添加延迟"""
        print("⏱️ 修复: 添加延迟...")
        await asyncio.sleep(2 ** task.retries if hasattr(task, 'retries') else 1)
        return task
    
    async def _fix_change_headers(self, task):
        """更换请求头"""
        print("📝 修复: 更换User-Agent...")
        task.headers = {
            **task.headers,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        return task
    
    async def _fix_increase_timeout(self, task):
        """增加超时时间"""
        print("⏰ 修复: 增加超时时间...")
        task.timeout = min(task.timeout * 2, 120)
        return task
    
    async def _fix_use_browser(self, task):
        """切换到浏览器模式"""
        print("🌐 修复: 切换到浏览器模式...")
        from ai_crawler import CrawlStrategy
        task.strategy = CrawlStrategy.BROWSER
        return task
    
    async def _fix_add_proxy(self, task):
        """添加代理"""
        print("🔀 修复: 尝试使用代理...")
        # 实际项目中配置代理
        return task
    
    async def _fix_retry_with_fallback(self, task):
        """降级重试"""
        print("📉 修复: 降级到简单模式...")
        task.instruction = ""  # 禁用LLM提取，简化处理
        return task
    
    def _get_suggestion(self, failure_type: FailureType) -> str:
        """获取建议"""
        suggestions = {
            FailureType.BLOCKED: "网站有反爬机制，建议使用浏览器模式或添加代理",
            FailureType.TIMEOUT: "页面加载慢，建议增加超时时间或简化请求",
            FailureType.NETWORK: "网络问题，建议检查连接或稍后重试",
            FailureType.PARSE_ERROR: "页面结构复杂，建议使用浏览器模式",
            FailureType.NOT_FOUND: "页面不存在，请检查URL",
        }
        return suggestions.get(failure_type, "未知错误，建议人工检查")
    
    def get_healing_stats(self) -> Dict:
        """获取修复统计"""
        if not self.failure_history:
            return {"message": "无失败记录"}
        
        type_counts = {}
        for record in self.failure_history:
            type_counts[record.failure_type.value] = type_counts.get(record.failure_type.value, 0) + 1
        
        fixed_count = sum(1 for r in self.failure_history if r.fix_applied)
        
        return {
            "total_failures": len(self.failure_history),
            "failures_by_type": type_counts,
            "fixes_applied": fixed_count,
            "recent_failures": [
                {
                    "url": r.url,
                    "type": r.failure_type.value,
                    "fix": r.fix_applied
                }
                for r in self.failure_history[-5:]
            ]
        }


async def healing_demo():
    """自修复演示"""
    from ai_crawler import AICrawler
    
    print("\n" + "=" * 50)
    print("🔧 自修复爬虫演示")
    print("=" * 50)
    
    crawler = AICrawler()
    healing_crawler = SelfHealingCrawler(crawler)
    
    # 演示：尝试访问一个可能失败的URL
    from ai_crawler import CrawlTask
    
    test_urls = [
        "https://httpbin.org/delay/10",  # 会超时
        "https://httpbin.org/status/403",  # 会被阻止
    ]
    
    for url in test_urls:
        print(f"\n🎯 测试: {url}")
        task = CrawlTask(url=url, timeout=2)
        result = await healing_crawler.crawl_with_healing(task)
        
        print(f"结果: {result}")
    
    # 统计
    print("\n📊 修复统计:")
    print(healing_crawler.get_healing_stats())


if __name__ == "__main__":
    asyncio.run(healing_demo())
