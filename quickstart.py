#!/usr/bin/env python3
"""
快速开始脚本 - 一键体验AI Smart Crawler
"""

import asyncio
import sys
sys.path.insert(0, '/tmp/ai-smart-crawler-user-friendly')

from ai_smart_crawler import SmartCrawlerSystem


async def quick_demo():
    """快速演示"""
    print("=" * 70)
    print("🚀 AI Smart Crawler - 快速开始")
    print("=" * 70)
    
    # 初始化
    print("\n1️⃣  初始化爬虫系统...")
    crawler = SmartCrawlerSystem()
    
    # 示例1: 爬取示例页面
    print("\n2️⃣  爬取示例页面...")
    try:
        content = await crawler.quick_fetch("https://httpbin.org/json")
        print(f"   ✅ 成功! 内容长度: {len(content)} 字符")
        print(f"   📄 预览: {content[:150]}...")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
    
    # 示例2: 批量爬取
    print("\n3️⃣  批量爬取测试...")
    urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/html",
    ]
    
    results = await crawler.batch_crawl(urls)
    for url, result in zip(urls, results):
        status = "✅" if result.success else "❌"
        size = len(result.markdown) if result.success else 0
        print(f"   {status} {url} ({size} chars)")
    
    # 完成
    print("\n" + "=" * 70)
    print("✨ 体验完成!")
    print("=" * 70)
    print("\n💡 下一步:")
    print("   • 使用 CLI: ai-crawler -u https://example.com")
    print("   • 查看示例: jupyter notebook examples/demo.ipynb")
    print("   • 阅读文档: README.md")


if __name__ == '__main__':
    asyncio.run(quick_demo())
