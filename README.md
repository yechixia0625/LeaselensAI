# LeaseLensAI

LeaseLensAI 是一个面向商业铺位评估的本地部署系统。用户上传铺位照片，输入业态、租金和面积后，系统会结合多智能体分析、经营决策平面图和真实周边地点数据，给出开店可行性判断。

## 功能概览

- 上传铺位图片并发起分析
- 多智能体实时输出分析日志
- 生成面向经营决策的空间 Blueprint
- 使用 Google Places 展示真实周边竞争环境
- 提供本地 What-if 模拟面板，快速调整租金与营收假设
- 支持 Docker 一键启动

## 技术栈

- Frontend: Next.js
- Backend: FastAPI
- Database: PostgreSQL + pgvector
- Cache: Redis
- Reverse Proxy: Nginx
- LLM: 智谱 GLM
- 地点数据: Google Places API (New)

## 快速开始

### 1. 环境要求

- Docker Desktop 或 Docker Engine
- Docker Compose
- 可用的智谱 GLM API Key
- 可用的 Google Places API (New) Key

### 2. 配置环境变量

先复制一份环境变量模板：

```bash
cp .env.example .env
```

至少需要配置以下字段：

- `LEASENS_LLM_API_KEY`
- `LEASENS_LLM_MODEL`
- `LEASENS_GOOGLE_PLACES_API_KEY`

如果你准备把系统放到公网测试，建议同时开启演示级登录：

- `LEASENS_DEMO_AUTH_ENABLED=true`
- `LEASENS_DEMO_AUTH_USERNAME`
- `LEASENS_DEMO_AUTH_PASSWORD`
- `LEASENS_DEMO_AUTH_SECRET`

当前项目默认使用智谱 GLM 系列模型，`.env.example` 中默认模型为：

```text
glm-4.1v-thinking-flash
```

### 3. 启动系统

对外公开部署、跨平台本地部署，统一使用这份 Compose 配置：

```bash
docker compose -f docker-compose.portable.yml up --build -d
```

启动后访问：

```text
http://localhost:8080/
```

### 4. 停止系统

```bash
docker compose -f docker-compose.portable.yml down
```

## 环境变量说明

### LLM 相关

- `LEASENS_LLM_API_KEY`：智谱 API Key
- `LEASENS_LLM_BASE_URL`：智谱接口地址
- `LEASENS_LLM_MODEL`：使用的 GLM 模型名称
- `LEASENS_LLM_TIMEOUT_SECONDS`：模型调用超时秒数

### Google Places 相关

- `LEASENS_GOOGLE_PLACES_API_KEY`：Google Places API (New) 服务端 Key
- `LEASENS_GOOGLE_PLACES_SEARCH_RADIUS_METERS`：附近搜索半径，单位米

### 演示登录相关

- `LEASENS_DEMO_AUTH_ENABLED`：是否启用公网测试登录
- `LEASENS_DEMO_AUTH_USERNAME`：统一访客用户名
- `LEASENS_DEMO_AUTH_PASSWORD`：统一访客密码
- `LEASENS_DEMO_AUTH_SECRET`：Cookie 签名密钥
- `LEASENS_DEMO_AUTH_COOKIE_NAME`：登录 Cookie 名称

### 代理相关

如果你的网络环境访问 Docker Hub、智谱或 Google API 需要代理，请按需配置：

- `DOCKER_BUILD_HTTP_PROXY`
- `DOCKER_BUILD_HTTPS_PROXY`
- `DOCKER_BUILD_NO_PROXY`
- `DOCKER_RUNTIME_HTTP_PROXY`
- `DOCKER_RUNTIME_HTTPS_PROXY`
- `DOCKER_RUNTIME_NO_PROXY`

如果你不需要代理，这些变量可以留空。

## Google Places API Key 申请

申请入口：

- Google Maps Platform 控制台：<https://console.cloud.google.com/google/maps-apis/start>
- Places API (New) 官方说明：<https://developers.google.com/maps/documentation/places/web-service/get-api-key>

申请时需要完成：

1. 创建或选择一个 Google Cloud 项目
2. 绑定 Billing Account
3. 启用 `Places API (New)`
4. 创建 API Key
5. 将 Key 限制为仅允许 `Places API (New)`

说明：

- 地址搜索和真实周边地点查询都依赖 Google Places API
- 该 Key 仅在后端使用，不应暴露到前端代码中

## 使用方式

启动后，典型流程如下：

1. 打开 `http://localhost:8080/`
2. 上传铺位图片
3. 填写业态、月租金、面积
4. 选择定位方式：
   - 使用当前位置
   - 输入地址并搜索定位
5. 点击分析
6. 在工作台中查看：
   - 四个 Agent 的实时分析输出
   - `Decision Plan` 决策型 Blueprint
   - `Live Market` 真实周边地图

如果启用了演示登录，用户访问首页后会先看到一个简单登录页。登录成功后才会进入上传分析界面。

## 部署验证

健康检查：

```bash
curl -i http://127.0.0.1:8080/api/v1/health
```

预期结果：

- 返回 `HTTP 200`

地址搜索检查：

```bash
curl -i -X POST http://127.0.0.1:8080/api/locations/autocomplete \
  -H 'Content-Type: application/json' \
  --data '{"input":"Shanghai","sessionToken":"session-token-1"}'
```

预期结果：

- 返回 `HTTP 200`
- 响应体中包含 `predictions`

## Compose 文件说明

仓库中包含两份 Compose 配置：

### `docker-compose.portable.yml`

这是公开部署的默认方案，适合：

- GitHub 用户本地部署
- Windows / macOS / Linux 跨平台使用
- 标准 Docker bridge 网络环境

特点：

- 容器间通过服务名通信
- `api` 连接 `db:5432` 与 `redis:6379`
- `nginx` 反代到 `api:8000`
- 不依赖 `network_mode: host`

### `docker-compose.yml`

这是维护者当前机器使用的本地配置，不作为公开部署默认入口。它可能包含针对特定宿主机网络、代理或端口环境的调整。

如果你只是从 GitHub 克隆项目并本地运行，请优先使用：

```bash
docker compose -f docker-compose.portable.yml up --build -d
```

## Windows 说明

- 建议使用 Docker Desktop
- 建议保持在 Linux containers 模式
- 推荐直接使用 `docker-compose.portable.yml`
- 如果宿主机代理运行在本机，通常应通过 `host.docker.internal` 供容器访问

## 常见问题

### 1. Docker 镜像拉取失败

表现：

- 拉取 `python`、`node`、`nginx`、`pgvector` 等镜像时报超时

排查：

- 检查 Docker 是否能访问 Docker Hub
- 如果需要代理，确认 `DOCKER_BUILD_HTTP_PROXY` 和 `DOCKER_BUILD_HTTPS_PROXY` 已正确配置

### 2. 地址搜索返回 503

表现：

- 页面提示 `Address suggestions are unavailable.`
- 或接口返回 `{"detail":"Location search is unavailable."}`

排查：

- 确认 `LEASENS_GOOGLE_PLACES_API_KEY` 已配置
- 确认 `Places API (New)` 已启用
- 确认运行时代理配置允许后端访问 Google Places

### 3. 页面上传图片时报 413

表现：

- 页面提示 `HTTP 413`

原因：

- 请求体超过 Nginx 限制

当前仓库中的 Nginx 配置已为图片上传调整过请求大小限制。如果你自行改过 Nginx 配置，需要同步检查 `client_max_body_size`。

### 4. 端口冲突

默认对外端口为：

- `8080`

如果宿主机该端口已被占用，可在 `.env` 中调整：

```text
PUBLIC_HTTP_PORT="8081"
```

### 5. 公网测试登录无法使用

排查：

- 确认 `LEASENS_DEMO_AUTH_ENABLED=true`
- 确认用户名、密码、签名密钥都已配置
- 修改 `.env` 后重新启动容器

说明：

- 这套登录只用于公网演示和临时测试
- 它不是生产级鉴权系统

## 安全说明

- 不要将真实 `.env` 提交到 Git 仓库
- `.env` 中的 LLM Key 和 Google Places Key 都应视为敏感信息
- 如果密钥曾经暴露，请立即在服务提供方后台轮换
