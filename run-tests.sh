#!/bin/bash
# 运行测试脚本

echo "🧪 AI Smart Crawler - 测试套件"
echo "================================"

# 检查pytest
if ! command -v pytest &> /dev/null; then
    echo "📦 安装测试依赖..."
    pip install pytest pytest-asyncio
fi

# 运行测试
echo ""
echo "🚀 运行测试..."
pytest tests/ -v

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 所有测试通过!"
else
    echo ""
    echo "❌ 部分测试失败"
fi
