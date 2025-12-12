# 使用 uv 管理 ChatDB Backend

## 快速开始

### 1. 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 2. 初始化项目

```bash
cd backend

# 运行设置脚本（创建 .env 和示例数据库）
uv run python setup.py

# 安装所有依赖
uv sync
```

### 3. 配置环境变量

编辑 `.env` 文件，设置你的 OpenRouter API key:
```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

### 4. 运行服务器

```bash
# 方法 1: 使用 Makefile
make run

# 方法 2: 使用 run.sh 脚本
./run.sh

# 方法 3: 直接使用 uv
PYTHONPATH=.. uv run python -m backend.main
```

## 常用命令

### 使用 Makefile

```bash
make install    # 安装依赖
make setup      # 初始化项目
make run        # 运行服务器
make verify     # 验证设置
make db         # 创建示例数据库
make test       # 运行测试
make clean      # 清理缓存
```

### 使用 uv 直接命令

```bash
# 安装依赖
uv sync

# 运行 Python 脚本
PYTHONPATH=.. uv run python -m backend.main

# 创建数据库
PYTHONPATH=.. uv run python -m backend.database.sample_data

# 运行验证
PYTHONPATH=.. uv run python scripts/verify.py
```

## 验证安装

运行验证脚本检查所有组件：

```bash
make verify

# 或
PYTHONPATH=.. uv run python scripts/verify.py
```

验证脚本会检查：
- ✓ 所有依赖包是否正确安装
- ✓ 后端模块是否可以导入
- ✓ 配置文件是否正确
- ✓ 数据库连接是否正常
- ✓ Agent graph 是否可以创建

## 项目结构

```
backend/
├── agent/          # LangGraph agent 工作流
├── tools/          # Agent 工具
├── database/       # 数据库管理
├── api/            # FastAPI 端点
├── config/         # 配置管理
├── scripts/        # 工具脚本
├── pyproject.toml  # uv 项目配置
├── uv.lock         # 依赖锁定文件
└── .env            # 环境变量（需要创建）
```

## 故障排除

### 模块导入错误

如果遇到 `ModuleNotFoundError: No module named 'backend'`，确保设置了 PYTHONPATH：

```bash
export PYTHONPATH=..:$PYTHONPATH
uv run python -m backend.main
```

### 依赖安装问题

```bash
# 清理并重新安装
rm -rf .venv
uv sync
```

### 数据库问题

```bash
# 重新创建示例数据库
make db
```

## 开发模式

uv 会自动管理虚拟环境（`.venv`），你不需要手动激活。

所有命令都使用 `uv run` 前缀，uv 会自动在正确的环境中执行。

