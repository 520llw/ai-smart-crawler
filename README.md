# AI Smart Crawler

> AI增强的智能爬虫系统，让数据提取像说话一样简单

[![PyPI version](https://badge.fury.io/py/ai-smart-crawler.svg)](https://badge.fury.io/py/ai-smart-crawler)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/)

**[English](README_EN.md)** | **中文**

---

## 🌟 核心特性

- 🤖 **AI驱动** - 自然语言描述，自动提取数据
- 🚀 **智能路由** - 自动选择最佳爬取策略
- 🔧 **自修复** - 自动诊断故障，智能重试
- 🧠 **知识库** - 自动构建可检索的知识库
- 📦 **开箱即用** - 一键安装，CLI命令行支持

---

## 🚀 快速开始

### 方式1: pip安装 (推荐)

```bash
# 安装
pip install ai-smart-crawler

# 使用CLI
ai-crawler -u https://example.com

# 批量爬取
ai-crawler -f urls.txt -o results.json
```

### 方式2: Docker

```bash
# 克隆仓库
git clone https://github.com/520llw/ai-smart-crawler.git
cd ai-smart-crawler

# Docker运行
docker-compose up

# 或直接进入容器
docker run -it ai-smart-crawler bash
```

### 方式3: 源码安装

```bash
git clone https://github.com/520llw/ai-smart-crawler.git
cd ai-smart-crawler
pip install -e .

# 快速体验
python quickstart.py
```

---

## 💡 使用示例

### CLI命令行

```bash
# 爬取单个网页
ai-crawler -u https://example.com

# 保存到文件
ai-crawler -u https://example.com -o output.md

# 批量爬取
ai-crawler -f urls.txt -o report.json -c 5

# 查看帮助
ai-crawler --help
```

### Python代码

```python
from ai_smart_crawler import SmartCrawlerSystem
import asyncio

async def main():
    # 初始化
    crawler = SmartCrawlerSystem()
    
    # 快速获取
    content = await crawler.quick_fetch("https://example.com")
    print(content)
    
    # 批量爬取
    urls = ["https://site1.com", "https://site2.com"]
    results = await crawler.batch_crawl(urls)

asyncio.run(main())
```

### Jupyter Notebook

打开 `examples/demo.ipynb` 查看交互式演示。

---

## 📦 安装

```bash
# 基础版
pip install ai-smart-crawler

# 完整版 (含所有高级功能)
pip install ai-smart-crawler[full]

# 开发版
pip install ai-smart-crawler[dev]
```

---

## 🏗️ 项目结构

```
ai-smart-crawler/
├── ai_smart_crawler/        # 核心包
│   ├── __init__.py
│   ├── simple_crawler.py    # 基础爬虫
│   ├── ai_crawler.py        # 完整版
│   ├── cli.py               # 命令行工具
│   ├── crawler_agent.py     # Agent模块
│   ├── rag_store.py         # 知识库存储
│   └── self_healing.py      # 自修复
├── examples/                # 示例
│   ├── demo.ipynb          # Jupyter演示
│   ├── urls.txt            # 示例URL列表
│   └── README.md
├── tests/                   # 测试
├── docs/                    # 文档
├── quickstart.py           # 快速开始脚本
├── Dockerfile              # Docker镜像
├── docker-compose.yml      # Docker Compose
├── setup.py                # 安装配置
└── README.md               # 本文件
```

---

## 📊 与传统爬虫对比

| 能力 | 传统爬虫 | AI Smart Crawler |
|:---|:---:|:---:|
| 开发方式 | XPath/CSS选择器 | 自然语言描述 |
| 维护成本 | 高 (页面改版需重写) | 低 (自适应) |
| 安装使用 | 复杂配置 | `pip install` 即用 |
| CLI支持 | 需自行开发 | 内置CLI |
| 批量处理 | 手动实现 | 内置并发控制 |
| 知识库 | 无 | 自动构建 |
| Docker | 自行配置 | 一键部署 |

---

## 🧪 测试

```bash
# 运行测试
pytest tests/ -v

# 生成覆盖率报告
pytest tests/ --cov=ai_smart_crawler --cov-report=html
```

---

## 🔒 安全与伦理

- 遵守目标网站的 `robots.txt`
- 建议请求频率 ≤ 1次/秒
- 不爬取受版权保护的内容
- 尊重个人隐私

---

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

```bash
# 贡献流程
1. Fork 本仓库
2. 创建分支 (git checkout -b feature/xxx)
3. 提交更改 (git commit -m 'Add xxx')
4. 推送分支 (git push origin feature/xxx)
5. 创建 Pull Request
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- 基于 [httpx](https://www.python-httpx.org/) 和 [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- 灵感来自 [Crawl4AI](https://github.com/unclecode/crawl4ai)

---

**Made with ❤️ by [GongJianwei](https://github.com/520llw)**

如果有问题，欢迎提交 [Issue](https://github.com/520llw/ai-smart-crawler/issues)
