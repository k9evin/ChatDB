# ChatDB Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/pyproject.toml backend/uv.lock ./
COPY backend/requirements.txt ./

# 安装 uv（如果使用 uv）
RUN pip install --no-cache-dir uv || echo "uv not available, using pip"

# 安装 Python 依赖
RUN if command -v uv &> /dev/null; then \
        uv sync --frozen || pip install -r requirements.txt; \
    else \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# 复制应用代码
COPY backend/ ./backend/
COPY .env* ./

# 设置 PYTHONPATH
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/docs', timeout=5)" || exit 1

# 启动命令
CMD ["python", "-m", "backend.main"]


