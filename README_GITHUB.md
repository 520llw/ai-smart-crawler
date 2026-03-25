# AI Smart Crawler System

> 一个AI增强的智能爬虫系统，融合大语言模型与传统爬虫技术，实现自然语言驱动的数据提取和知识库构建。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](#english) | [中文](#中文)

---

## 中文

### 🌟 核心特性

| 特性 | 说明 |
|:---|:---|
| 🤖 **AI驱动** | 自然语言描述提取需求，AI自动解析 |
| 🔧 **自修复** | 自动诊断故障并切换策略 |
| 🧠 **知识库** | 自动构建可检索的知识库 |
| 📊 **结构化** | 自动输出JSON/Schema格式 |
| 🚀 **智能路由** | 自动选择最佳爬取策略 |
| 📝 **Markdown** | 生成干净的Markdown内容 |

### 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/GongJianwei/ai-smart-crawler.git
cd ai-smart-crawler

# 安装依赖
pip install -r requirements.txt

# 运行演示
python simple_crawler.py
```

### 💡 使用示例

```python
from simple_crawler import SmartCrawlerSystem
import asyncio

async def main():
    # 初始化
    crawler = SmartCrawlerSystem()
    
    # 快速获取网页
    content = await crawler.quick_fetch("https://example.com")
    print(content)
    
    # 批量爬取
    urls = ["https://site1.com", "https://site2.com"]
    results = await crawler.batch_crawl(urls)

asyncio.run(main())
```

### 📊 与传统爬虫对比

| 能力 | 传统爬虫 | AI Smart Crawler |
|:---|:---:|:---:|
| 开发效率 | 低 (需写选择器) | 高 (自然语言) |
| 维护成本 | 高 (页面改版需重写) | 低 (自适应) |
| 数据提取 | 规则匹配 | AI理解 |
| 知识积累 | 无 | 自动构建 |
| 智能问答 | 无 | 支持 |

### 📁 项目结构

```
ai-smart-crawler/
├── simple_crawler.py          # 简化版入口
├── ai_crawler_system.py       # 完整版入口
├── medical_kb_final.py        # 知识库示例
├── README.md                  # 本文档
├── LICENSE                    # MIT许可证
└── requirements.txt           # 依赖列表
```

---

## English

### 🌟 Core Features

| Feature | Description |
|:---|:---|
| 🤖 **AI-Powered** | Natural language driven extraction |
| 🔧 **Self-Healing** | Auto-diagnose and retry |
| 🧠 **Knowledge Base** | Auto-build searchable knowledge base |
| 📊 **Structured** | JSON/Schema output |
| 🚀 **Smart Router** | Auto-select best strategy |
| 📝 **Markdown** | Clean markdown generation |

### 🚀 Quick Start

```bash
# Clone
git clone https://github.com/GongJianwei/ai-smart-crawler.git
cd ai-smart-crawler

# Install
pip install -r requirements.txt

# Run demo
python simple_crawler.py
```

### 💡 Usage

```python
from simple_crawler import SmartCrawlerSystem
import asyncio

async def main():
    crawler = SmartCrawlerSystem()
    
    # Quick fetch
    content = await crawler.quick_fetch("https://example.com")
    
    # Batch crawling
    urls = ["https://site1.com", "https://site2.com"]
    results = await crawler.batch_crawl(urls)

asyncio.run(main())
```

---

## 🔒 Security & Ethics

### 使用规范

1. **遵守robots.txt** - 爬取前检查网站爬虫协议
2. **合理频率** - 建议每秒不超过1个请求
3. **尊重版权** - 不爬取受版权保护的内容
4. **隐私保护** - 不爬取个人隐私信息

### Security Features

- Request timeout (default 30s)
- User-Agent rotation
- Content length limit
- Error handling without info leakage

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🤝 Contributing

Pull requests are welcome! 

## 🙏 Acknowledgments

- Built on [httpx](https://www.python-httpx.org/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- Inspired by [Crawl4AI](https://github.com/unclecode/crawl4ai)

---

**Made with ❤️ by [GongJianwei](https://github.com/GongJianwei)**
