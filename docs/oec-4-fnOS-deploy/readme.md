# HomeLab Monitor - OEC-4 fnOS 部署

将 [HomeLab Monitor](https://github.com/SikamikanikoBG/homelab-monitor) 部署到 RK3566 OECT-4 fnOS 主机。

## 部署状态

**已完成** - 容器运行正常，版本 0.14.4

| 服务 | 地址 | 状态 |
|------|------|------|
| Dashboard | http://192.168.123.54:9800 | 正常 |
| MCP Server | http://192.168.123.54:9810/mcp | 正常 |

## 目录结构

```
docs/oec-4-fnOS-deploy/
├── config/                         # 部署配置文件
│   ├── docker-compose.yml          # Docker Compose 配置 (使用 env 变量)
│   └── .env                        # 环境变量 (端口、镜像名、采集参数)
├── scripts/                        # 自动化脚本
│   └── upload_config.py            # SCP 上传脚本 (paramiko)
├── docs/                           # 文档
│   ├── progress.md                 # 部署进度跟踪
│   └── user-guide.md               # 最终用户操作手册
├── password.csv                    # 主机凭据 (勿提交到公共仓库)
└── readme.md                       # 本文件
```

## 文档导航

| 文档 | 说明 |
|------|------|
| [操作手册](docs/user-guide.md) | 部署步骤、日常运维、故障排查指南 |
| [进度记录](docs/progress.md) | 部署各步骤的执行状态和时间记录 |
| [docker-compose.yml](config/docker-compose.yml) | 容器编排配置 |
| [.env](config/.env) | 环境变量配置 |
| [upload_config.py](scripts/upload_config.py) | 自动化 SCP 上传脚本 |

## 快速操作

### 更新配置并重启

```bash
# 1. 在本地编辑 config/ 下的文件
# 2. 上传到远程主机
python scripts/upload_config.py

# 3. 远程重启容器
python "C:\Users\liujianglong\.qoder\skills\ssh-unattended\scripts\ssh_command.py" \
  "cd /vol1/docker/mycontainers/homelab-monitor && docker compose up -d" \
  --csv "docs/oec-4-fnOS-deploy/password.csv"
```

### 查看容器状态

```bash
python "C:\Users\liujianglong\.qoder\skills\ssh-unattended\scripts\ssh_command.py" \
  "docker ps --filter name=homelab-monitor && curl -sf http://127.0.0.1:9800/healthz" \
  --csv "docs/oec-4-fnOS-deploy/password.csv"
```

## 环境信息

| 项目 | 值 |
|------|-----|
| 主机 | 192.168.123.54 (RK3566 OECT-4 fnOS) |
| 架构 | aarch64 (ARM64) |
| 工作目录 | `/vol1/docker/mycontainers/homelab-monitor` |
| 数据目录 | `/vol1/docker/mycontainers/homelab-monitor/data` |
| 网络代理 | 192.168.123.222:7890 (拉取镜像时使用) |
