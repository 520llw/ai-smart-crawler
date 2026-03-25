# AI Smart Crawler 测试套件

本目录包含项目的测试代码。

## 运行测试

### 安装测试依赖
```bash
pip install pytest pytest-asyncio
```

### 运行所有测试
```bash
pytest tests/ -v
```

### 运行特定测试
```bash
pytest tests/test_crawler.py::TestSimpleCrawler -v
```

### 生成测试报告
```bash
pytest tests/ --cov=ai_smart_crawler --cov-report=html
```

## 测试结构

```
tests/
├── test_crawler.py      # 核心爬虫测试
├── test_cli.py          # CLI测试
└── test_knowledge.py    # 知识库测试
```

## 编写新测试

```python
import pytest
from ai_smart_crawler import SmartCrawlerSystem

@pytest.mark.asyncio
async def test_new_feature():
    crawler = SmartCrawlerSystem()
    result = await crawler.quick_fetch("https://example.com")
    assert result is not None
```
