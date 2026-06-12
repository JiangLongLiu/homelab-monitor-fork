# HomeLab Monitor - OEC-4 fnOS 部署操作手册

## 概述

本手册描述如何在 RK3566 OECT-4 fnOS 主机上部署和管理 HomeLab Monitor 容器。

### 环境信息

| 项目 | 值 |
|------|-----|
| 主机 IP | 192.168.123.54 |
| 主机架构 | aarch64 (ARM64) |
| SSH 端口 | 22 |
| 工作目录 | `/vol1/docker/mycontainers/homelab-monitor` |
| Dashboard 地址 | http://192.168.123.54:9800 |
| MCP Server 地址 | http://192.168.123.54:9810/mcp |
| Docker 版本 | v28.2.2 |
| Docker Compose 版本 | v2.40.3 |

---

## 首次部署

### 前提条件

1. fnOS 主机已安装 Docker 和 Docker Compose
2. 能够 SSH 登录到主机 (root 账户)
3. 如主机无法直连外网，需要配置 HTTP 代理

### 步骤 1: 创建工作目录

```bash
ssh root@192.168.123.54
mkdir -p /vol1/docker/mycontainers/homelab-monitor/data
cd /vol1/docker/mycontainers/homelab-monitor
```

### 步骤 2: 上传配置文件

将 `config/` 目录下的 `docker-compose.yml` 和 `.env` 文件上传到远程主机:

```bash
# 方法1: 使用 upload_config.py 脚本 (推荐)
python scripts/upload_config.py

# 方法2: 手动 scp
scp config/docker-compose.yml config/.env root@192.168.123.54:/vol1/docker/mycontainers/homelab-monitor/
```

### 步骤 3: 拉取镜像

```bash
# 直连拉取
cd /vol1/docker/mycontainers/homelab-monitor
docker compose pull

# 通过代理拉取 (如无法直连)
HTTP_PROXY=http://<代理IP>:<代理端口> \
HTTPS_PROXY=http://<代理IP>:<代理端口> \
docker compose pull
```

### 步骤 4: 启动容器

```bash
cd /vol1/docker/mycontainers/homelab-monitor
docker compose up -d
```

### 步骤 5: 验证部署

```bash
# 检查容器状态
docker ps --filter name=homelab-monitor

# 健康检查
curl http://127.0.0.1:9800/healthz
# 预期输出: {"status":"ok","version":"x.x.x"}
```

---

## 日常运维

### 查看容器状态

```bash
docker ps --filter name=homelab-monitor
docker logs homelab-monitor --tail 50
```

### 重启容器

```bash
cd /vol1/docker/mycontainers/homelab-monitor
docker compose restart
```

### 更新镜像

```bash
cd /vol1/docker/mycontainers/homelab-monitor

# 拉取最新镜像 (如需代理加上 HTTP_PROXY/HTTPS_PROXY)
HTTP_PROXY=http://<代理IP>:<代理端口> \
HTTPS_PROXY=http://<代理IP>:<代理端口> \
docker compose pull

# 重建容器 (自动使用新镜像)
docker compose up -d
```

### 停止容器

```bash
cd /vol1/docker/mycontainers/homelab-monitor
docker compose down
```

### 查看资源使用

```bash
docker stats homelab-monitor --no-stream
```

---

## 配置修改

### 修改端口

编辑 `.env` 文件:

```env
DASHBOARD_PORT=9801   # 修改 dashboard 端口
MCP_PORT=9811          # 修改 MCP 端口
```

然后重新上传并重启:

```bash
python scripts/upload_config.py
ssh root@192.168.123.54 "cd /vol1/docker/mycontainers/homelab-monitor && docker compose up -d"
```

### 修改采集间隔 / 数据保留天数

编辑 `.env` 文件中的对应变量:

```env
SAMPLE_INTERVAL=5      # 采集间隔改为 5 秒
RETENTION_DAYS=365     # 数据保留 365 天
```

---

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker logs homelab-monitor

# 检查端口冲突
ss -tlnp | grep -E '9800|9810'

# 检查磁盘空间
df -h /vol1
```

### 健康检查失败

```bash
# 手动测试
curl -v http://127.0.0.1:9800/healthz

# 检查容器内部状态
docker exec homelab-monitor ps aux
```

### 镜像拉取失败

```bash
# 确认代理可用
curl -x http://<代理IP>:<代理端口> http://httpbin.org/ip

# 使用临时环境变量重试
HTTP_PROXY=http://<代理IP>:<代理端口> \
HTTPS_PROXY=http://<代理IP>:<代理端口> \
docker pull sikamikaniko123/homelab-monitor:latest
```

### 数据目录权限问题

```bash
# 检查 data 目录权限
ls -la /vol1/docker/mycontainers/homelab-monitor/data/

# 修复权限 (容器以 root 运行)
chmod 755 /vol1/docker/mycontainers/homelab-monitor/data/
```

---

## 数据备份

SQLite 数据库存储在 `./data` 目录中:

```bash
# 备份数据
cp -r /vol1/docker/mycontainers/homelab-monitor/data/ /vol1/docker/backups/homelab-monitor-data-$(date +%Y%m%d)
```

---

## MCP Server 使用

HomeLab Monitor 内置只读 MCP Server，可通过以下方式连接:

```bash
# HTTP 方式
claude mcp add --transport http homelab http://192.168.123.54:9810/mcp

# stdio 方式
docker run -i --rm \
  -e HOMELAB_MONITOR_URL=http://192.168.123.54:9800 \
  -e MCP_TRANSPORT=stdio \
  sikamikaniko123/homelab-monitor python /app/mcp_server.py
```

可用的 MCP 工具: `list_hosts`, `get_host`, `get_snapshot`, `get_containers`, `get_services`, `get_memory`, `get_gpu`, `get_ai_models`, `get_history`, `get_events`, `get_alerts`, `scan_disk`
