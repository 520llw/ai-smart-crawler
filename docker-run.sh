#!/bin/bash
# Docker快速启动脚本

echo "🐳 AI Smart Crawler - Docker快速启动"
echo "======================================"

# 构建镜像
echo "📦 构建Docker镜像..."
docker build -t ai-smart-crawler:latest .

# 运行快速开始
echo ""
echo "🚀 运行快速开始..."
docker run --rm -it ai-smart-crawler:latest

# 或者进入交互模式
echo ""
echo "💡 进入交互模式:"
echo "   docker run --rm -it ai-smart-crawler:latest bash"
echo ""
echo "💡 使用CLI:"
echo "   docker run --rm ai-smart-crawler:latest ai-crawler -u https://example.com"
