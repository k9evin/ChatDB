# ChatDB Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./backend/

# 设置 PYTHONPATH
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8000

# 启动命令
# Use single worker for WebSocket support, but with proper async configuration
# --timeout-keep-alive ensures connections stay alive
# --limit-concurrency prevents overload
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "75", "--limit-concurrency", "1000"]









