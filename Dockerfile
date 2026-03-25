# AI Smart Crawler Dockerfile
# 一键部署AI爬虫系统

FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY setup.py .
COPY ai_smart_crawler/ ./ai_smart_crawler/
COPY quickstart.py .
COPY examples/ ./examples/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装项目
RUN pip install -e .

# 创建输出目录
RUN mkdir -p /app/output

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 默认命令
CMD ["python", "quickstart.py"]
