#!/usr/bin/env python3
"""
AI Smart Crawler CLI
命令行工具，方便用户快速使用
"""

import argparse
import asyncio
import sys
import json
from urllib.parse import urlparse

# 尝试导入包内模块
try:
    from ai_smart_crawler import SmartCrawlerSystem
except ImportError:
    sys.path.insert(0, '/tmp/ai-smart-crawler-user-friendly')
    from ai_smart_crawler import SmartCrawlerSystem


def validate_url(url):
    """验证URL格式"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


async def fetch_url(url, output=None, format='markdown'):
    """获取单个URL"""
    print(f"🚀 正在爬取: {url}")
    
    crawler = SmartCrawlerSystem()
    result = await crawler.quick_fetch(url)
    
    if result.startswith('Error') or result.startswith('❌'):
        print(f"❌ 爬取失败: {result}")
        return False
    
    print(f"✅ 爬取成功! 内容长度: {len(result)} 字符")
    
    # 输出到文件或屏幕
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"💾 已保存到: {output}")
    else:
        print("\n" + "="*60)
        print("📄 内容预览:")
        print("="*60)
        print(result[:1000])
        if len(result) > 1000:
            print(f"\n... (还有 {len(result)-1000} 字符)")
    
    return True


async def batch_fetch(urls, output=None, max_concurrent=3):
    """批量爬取"""
    print(f"🚀 批量爬取 {len(urls)} 个URL")
    print(f"   并发数: {max_concurrent}")
    
    crawler = SmartCrawlerSystem()
    results = await crawler.batch_crawl(urls, max_concurrent=max_concurrent)
    
    # 整理结果
    report = []
    for url, result in zip(urls, results):
        status = "✅" if result.success else "❌"
        size = len(result.markdown) if result.success else 0
        report.append({
            'url': url,
            'success': result.success,
            'size': size,
            'title': result.metadata.get('title', 'N/A')
        })
        print(f"{status} {url} ({size} chars)")
    
    # 保存报告
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n💾 报告已保存: {output}")
    
    # 统计
    success_count = sum(1 for r in results if r.success)
    print(f"\n📊 统计: {success_count}/{len(urls)} 成功 ({success_count/len(urls)*100:.0f}%)")
    
    return success_count == len(urls)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AI Smart Crawler - 智能爬虫系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 爬取单个网页
  ai-crawler -u https://example.com
  
  # 保存到文件
  ai-crawler -u https://example.com -o output.md
  
  # 批量爬取
  ai-crawler -f urls.txt -o report.json
  
  # 设置并发数
  ai-crawler -f urls.txt -c 5
        """
    )
    
    parser.add_argument('-u', '--url', 
                       help='单个URL地址')
    parser.add_argument('-f', '--file',
                       help='包含URL列表的文件 (每行一个URL)')
    parser.add_argument('-o', '--output',
                       help='输出文件路径')
    parser.add_argument('-c', '--concurrent', type=int, default=3,
                       help='并发数 (默认: 3)')
    parser.add_argument('--format', choices=['markdown', 'text', 'json'], default='markdown',
                       help='输出格式 (默认: markdown)')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0.0',
                       help='显示版本')
    
    args = parser.parse_args()
    
    # 检查参数
    if not args.url and not args.file:
        parser.print_help()
        print("\n❌ 错误: 请提供 -u URL 或 -f 文件路径")
        sys.exit(1)
    
    # 单URL模式
    if args.url:
        if not validate_url(args.url):
            print(f"❌ 无效的URL: {args.url}")
            sys.exit(1)
        
        success = asyncio.run(fetch_url(args.url, args.output, args.format))
        sys.exit(0 if success else 1)
    
    # 批量模式
    if args.file:
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            # 验证URL
            valid_urls = [u for u in urls if validate_url(u)]
            invalid_urls = [u for u in urls if not validate_url(u)]
            
            if invalid_urls:
                print(f"⚠️  忽略 {len(invalid_urls)} 个无效URL")
            
            if not valid_urls:
                print("❌ 没有有效的URL")
                sys.exit(1)
            
            print(f"📋 读取到 {len(valid_urls)} 个有效URL")
            success = asyncio.run(batch_fetch(valid_urls, args.output, args.concurrent))
            sys.exit(0 if success else 1)
            
        except FileNotFoundError:
            print(f"❌ 文件不存在: {args.file}")
            sys.exit(1)


if __name__ == '__main__':
    main()
