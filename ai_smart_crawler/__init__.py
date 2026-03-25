"""
AI Smart Crawler - 智能爬虫系统

一个AI增强的智能爬虫系统，融合大语言模型与传统爬虫技术。
"""

__version__ = "1.0.0"
__author__ = "GongJianwei"
__email__ = "2407010703@qq.com"

# 核心类导入
from .simple_crawler import SmartCrawlerSystem, SimpleAICrawler, CrawlTask, CrawlResult

# 可选导入（如果依赖存在）
try:
    from .ai_crawler import AICrawler
except ImportError:
    pass

try:
    from .crawler_agent import CrawlerAgent, AgentTask
except ImportError:
    pass

try:
    from .rag_store import RAGStore, CrawlKnowledgeBase
except ImportError:
    pass

try:
    from .self_healing import SelfHealingCrawler
except ImportError:
    pass

__all__ = [
    'SmartCrawlerSystem',
    'SimpleAICrawler',
    'CrawlTask',
    'CrawlResult',
    'AICrawler',
    'CrawlerAgent',
    'AgentTask',
    'RAGStore',
    'CrawlKnowledgeBase',
    'SelfHealingCrawler',
]
