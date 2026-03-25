# AI Smart Crawler Examples

本目录包含各种使用示例。

## 快速开始

### 1. CLI命令行
```bash
# 爬取单个网页
ai-crawler -u https://example.com

# 批量爬取
ai-crawler -f urls.txt -o report.json

# 设置并发数
ai-crawler -f urls.txt -c 5 -o results.json
```

### 2. Python代码
```python
from ai_smart_crawler import SmartCrawlerSystem
import asyncio

async def main():
    crawler = SmartCrawlerSystem()
    
    # 单个网页
    content = await crawler.quick_fetch("https://example.com")
    print(content)
    
    # 批量爬取
    urls = ["https://site1.com", "https://site2.com"]
    results = await crawler.batch_crawl(urls)

asyncio.run(main())
```

### 3. Jupyter Notebook
打开 `demo.ipynb` 查看交互式演示。

## 示例文件

- `demo.ipynb` - Jupyter交互式演示
- `urls.txt` - 示例URL列表
- `batch_crawl.py` - 批量爬取示例
- `custom_task.py` - 自定义任务示例
