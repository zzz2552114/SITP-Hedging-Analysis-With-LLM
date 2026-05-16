按本文步骤操作可以在本地启动后端（uvicorn）和前端（Vite），可以看到前后端交互。

# SITP-Hedging-Analysis-With-LLM — 使用说明

## 简要说明
按顺序执行下面步骤可在本地运行：
- 后端：FastAPI + Tortoise ORM（使用 MySQL），运行在默认端口 8000（uvicorn）。
- 前端：Vite（默认端口 5173）。
前端通过 /api 路径调用后端接口（仓库后端代码已配置 CORS allow_origins=["*"]）。

---

## 先决条件
- Git
- Node.js（建议 >=16）和 npm / yarn / pnpm
- Python 3.10+（建议 3.10/3.11）
- MySQL 实例（本地或远程）
- 可选：LLM 服务的 API Key（若使用自动化解析）

---

## 1. 获取源码
```bash
git clone https://gitee.com/zzz2552114/SITP-Hedging-Analysis-With-LLM
cd SITP-Hedging-Analysis-With-LLM
```

---

## 2. 后端（backend）设置与启动

### 2.1 进入后端并创建虚拟环境
```bash
cd backend
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 2.2 安装依赖

在python终端安装依赖：
```bash
pip install -r requirements.txt
```

### 2.3 配置数据库（MySQL）
后端数据库配置位于 `backend/app/database.py`。默认值：
- DB_USER: root
- DB_PASSWORD: （仓库有默认值，请改为自己的）
- DB_HOST: 127.0.0.1
- DB_PORT: 3306
- DB_NAME: sitp_hedging

在 shell 中设置环境变量（示例）：

Linux / macOS:
```bash
export DB_USER=myuser
export DB_PASSWORD='mypassword'
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_NAME=sitp_hedging
```

Windows PowerShell:
```powershell
$env:DB_USER="myuser"
$env:DB_PASSWORD="mypassword"
$env:DB_HOST="127.0.0.1"
$env:DB_PORT="3306"
$env:DB_NAME="sitp_hedging"
```

> 注意：仓库中 `backend/app/database.py` 会从环境变量读取这些值。不要在生产中提交明文密码。

### 2.4 初始化迁移（aerich）并迁移数据库
仓库 `backend/pyproject.toml` 已包含 tortoise 的配置引用 `app.database.TORTOISE_ORM`。在 `backend` 目录下运行：

（如果你还未用 aerich 初始化迁移配置）
```bash
# 初始化 aerich（只需一次）
aerich init -t app.database.TORTOISE_ORM

# 生成迁移
aerich migrate --name "init"

# 应用迁移
aerich upgrade
```

说明：如果仓库已包含 `migrations` 目录（仓库里有可能已有），你可能只需执行 `aerich upgrade`。

### 2.5 启动后端服务
在仓库根目录或 `backend` 目录运行：
```bash
# 在仓库根目录推荐使用：
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 或在 backend 目录使用：
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- 后端 OpenAPI（如启用）通常在： http://localhost:8000/docs 或 http://localhost:8000/redoc
- 常用后端路由示例：`/api/data/pdfs`、`/api/cralw`、`/api/analyze`（请参考 `backend/main.py` 源码以获取确切路由）

---

## 3. 前端（frontend）设置与启动

### 3.1 安装依赖
```bash
cd frontend
npm install
# 或者使用 yarn:
# yarn
# pnpm:
# pnpm install
```

### 3.2 启动开发服务器（Vite）
```bash
npm run dev
```
默认开发地址通常为： http://localhost:5173

如果 `package.json` 中脚本不同，请查看 `frontend/package.json` 中 `scripts` 字段并使用对应命令（例如 `yarn dev`）。

---

## 4. 验证前后端工作
- 打开浏览器访问前端地址，例如：http://localhost:5173
- 后端控制台（uvicorn）会显示收到的 API 请求。
- 测试后端接口（示例）：
  - `GET http://localhost:8000/api/data/pdfs` —— 列出 data/pdfs 中的 PDF（如有）
  - `GET http://localhost:8000/docs` —— 查看 OpenAPI（若启用）
- 若前端在页面中发起 API 请求，确保前端请求的目标为 `http://localhost:8000/api/...` 或使用代理设置。

---

## 5. 关于解析/LLM / worker
- 仓库包含 `backend/app/worker.py`，示例函数 `process_unparsed_announcements` 演示如何遍历未解析公告、读取本地 PDF、并（假设）调用 LLM 解析后写入 DB。
- 若你要启用自动解析，需要：
  - 准备 LLM API Key 并在调用处提供（后端路由或 worker 接口中按需要传入）。
  - 将仓库 `dev` 中的解析脚本（如 `sitp_recheck_2`）调整为可被调用并返回结构化数据，或修改 worker 以适配 LLM SDK。
- worker 是异步函数，生产环境中可用定时任务或后台任务队列触发。

---

## 6. 常见故障与排查
- 数据库连接失败
  - 检查 MySQL 是否运行，确认用户名/密码/主机/端口与环境变量一致。
  - 使用 mysql 客户端本地测试连接： `mysql -uUSER -p -h HOST -P PORT`
- aerich 迁移问题
  - 确认 tortoise 配置 `app.database.TORTOISE_ORM` 与 `pyproject.toml` 中一致。
  - 若迁移失败，删除并重新生成迁移（务必备份生产数据）。
- 依赖安装错误
  - 确认虚拟环境已激活并升级 pip： `pip install -U pip`
- 前端不显示或与后端通信失败
  - 确认 Vite 已启动并监听端口；检查浏览器控制台与网络请求。
  - 后端已有 CORS allow_origins=["*"]（默认允许所有来源），通常不会出现 CORS 问题。

---

## 7. 安全与生产建议
- 不要把敏感凭证提交到代码库。使用环境变量或密钥管理系统保存 DB 密码、API Key。
- 生产后端建议使用 Uvicorn + Gunicorn 的多 worker 部署，前端用静态 CDN 或 nginx 托管并配置 HTTPS。
- 定期更新依赖并审计安全问题。

---
