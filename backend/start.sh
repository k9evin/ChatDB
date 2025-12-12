#!/bin/bash
# 一键启动 ChatDB 后端服务
# 自动检查并设置环境，然后启动服务器

set -e

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$SCRIPT_DIR"

echo "🚀 ChatDB 后端启动脚本"
echo "===================="

# 1. 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 文件..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ 已从 .env.example 创建 .env 文件"
        echo "⚠️  请编辑 .env 文件，设置你的 OPENROUTER_API_KEY"
    else
        echo "❌ 未找到 .env.example 文件"
        exit 1
    fi
fi

# 2. 检查依赖
if ! command -v uv &> /dev/null; then
    echo "📦 检测到未安装 uv，尝试使用 pip..."
    if ! command -v python3 &> /dev/null; then
        echo "❌ 未找到 Python3，请先安装 Python 3.11+"
        exit 1
    fi
    
    # 使用 pip 安装依赖
    if [ ! -d "venv" ]; then
        echo "📦 创建虚拟环境..."
        python3 -m venv venv
    fi
    
    echo "📦 安装依赖..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    echo "🚀 启动服务器（使用 pip）..."
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    python -m backend.main
else
    # 使用 uv
    echo "📦 检查依赖..."
    if [ ! -f "uv.lock" ] || [ ! -d ".venv" ]; then
        echo "📦 安装依赖..."
        uv sync
    fi
    
    # 3. 检查数据库
    if [ ! -f "demo_database.db" ]; then
        echo "🗄️  创建示例数据库..."
        PYTHONPATH="$PROJECT_ROOT" uv run python -m backend.database.sample_data || echo "⚠️  数据库创建失败，但继续启动..."
    fi
    
    # 4. 启动服务器
    echo "🚀 启动服务器..."
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    uv run python -m backend.main
fi


