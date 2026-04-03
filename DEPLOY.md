# ZZZAi Bot 部署指南

## 目录

- [系统要求](#系统要求)
- [架构概览](#架构概览)
- [环境准备](#环境准备)
- [NapCat 安装配置](#napcat-安装配置)
- [Bot 部署](#bot-部署)
- [启动服务](#启动服务)
- [运维管理](#运维管理)
- [常见问题](#常见问题)

---

## 系统要求

### 最低配置

| 项目 | 要求 |
|------|------|
| CPU | 2核 |
| 内存 | 2GB |
| 存储 | 10GB |
| 系统 | Ubuntu 20.04+ / Debian 11+ / CentOS 8+ |

### 推荐配置

| 项目 | 要求 |
|------|------|
| CPU | 2核+ |
| 内存 | 4GB |
| 存储 | 20GB SSD |
| 系统 | Ubuntu 22.04 LTS |

---

## 架构概览

```
┌─────────────────────────────────────────────────────────┐
│                      Linux 服务器                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ┌─────────────┐         WebSocket        ┌─────────┐ │
│   │   NapCat    │ ◄──────────────────────► │ NoneBot │ │
│   │  (QQ协议端)  │      127.0.0.1:3000      │  (Bot)  │ │
│   │   ~300MB    │                          │ ~400MB  │ │
│   └─────────────┘                          └─────────┘ │
│         │                                        │      │
│         ▼                                        ▼      │
│   ┌─────────────┐                          ┌─────────┐ │
│   │  QQ账号状态  │                          │ SQLite  │ │
│   │  (扫码登录)  │                          │ChromaDB │ │
│   └─────────────┘                          └─────────┘ │
│                                                         │
│   内存占用: 系统(~300MB) + NapCat(~300MB) + Bot(~400MB) │
│   总计: ~1GB，剩余 ~1GB                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 环境准备

### 1. 更新系统

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS
sudo yum update -y
```

### 2. 安装基础依赖

```bash
# Ubuntu/Debian
sudo apt install -y curl wget git vim htop tmux

# CentOS
sudo yum install -y curl wget git vim htop tmux
```

### 3. 安装 Python 3.10+

```bash
# Ubuntu 22.04 (自带 Python 3.10)
sudo apt install -y python3 python3-pip python3-venv

# Ubuntu 20.04 (需要添加 PPA)
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
```

### 4. 安装 Node.js 18+ (NapCat依赖)

```bash
# 使用 NodeSource 安装
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
node --version  # v18.x.x
npm --version
```

### 5. 安装 Docker (推荐用于NapCat)

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER

# 重新登录后验证
docker --version
```

### 6. 配置 Swap (推荐)

```bash
# 创建 2GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 验证
free -h
```

---

## NapCat 安装配置

### 方式一：Docker 部署 (推荐)

#### 1. 创建数据目录

```bash
mkdir -p ~/napcat/data
mkdir -p ~/napcat/config
```

#### 2. 拉取镜像

```bash
docker pull mlikiowa/napcat-docker:latest
```

#### 3. 创建配置文件

```bash
cat > ~/napcat/config/onebot11.json << 'EOF'
{
  "http": {
    "enable": false,
    "host": "0.0.0.0",
    "port": 3000,
    "secret": "",
    "enableHeart": false,
    "enablePost": false
  },
  "ws": {
    "enable": true,
    "host": "0.0.0.0",
    "port": 3001
  },
  "reverseWs": {
    "enable": true,
    "urls": [
      {
        "address": "ws://127.0.0.1:8080/onebot/v11/ws",
        "enable": true
      }
    ]
  },
  "debug": false,
  "heartInterval": 30000,
  "messagePostFormat": "array",
  "enableLocalFile2Url": false,
  "musicSignUrl": "",
  "reportSelfMessage": false,
  "token": ""
}
EOF
```

#### 4. 启动容器

```bash
docker run -d \
  --name napcat \
  --restart=always \
  --memory="400m" \
  --memory-swap="600m" \
  -p 3001:3001 \
  -p 6099:6099 \
  -v ~/napcat/data:/app/.config/QQ \
  -v ~/napcat/config:/app/napcat/config \
  mlikiowa/napcat-docker:latest
```

#### 5. 扫码登录

```bash
# 查看日志获取二维码
docker logs -f napcat

# 或访问 Web 界面扫码
# http://服务器IP:6099
```

### 方式二：直接安装

#### 1. 克隆项目

```bash
cd ~
git clone https://github.com/NapNeko/NapCatQQ.git
cd NapCatQQ
```

#### 2. 安装依赖

```bash
npm install
```

#### 3. 配置

```bash
mkdir -p config
cp config/onebot11.json.example config/onebot11.json
# 编辑配置文件，内容同上
vim config/onebot11.json
```

#### 4. 启动

```bash
npm run start
```

---

## Bot 部署

### 1. 克隆项目

```bash
cd ~
git clone <your-repo-url> ZZZAi
cd ZZZAi
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置文件

```bash
# 创建配置目录
mkdir -p config

# 创建配置文件
cat > config/config.yaml << 'EOF'
# Bot 基础配置
bot:
  name: "ZZZAi"
  superusers:
    - "你的QQ号"

# LLM 配置
llm:
  provider: "openai"
  api_key: "你的API密钥"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"

# 存储配置
storage:
  database: "./data/zzzai.db"
  vector_path: "./data/memory/"

# 日志配置
log:
  level: "INFO"
  file: "./logs/bot.log"

# NapCat 连接
adapter:
  onebot:
    ws_urls:
      - "ws://127.0.0.1:3001"
EOF
```

### 5. 创建必要目录

```bash
mkdir -p data logs
```

### 6. 验证配置

```bash
python -c "from src.utils import load_config; load_config(); print('配置OK')"
```

---

## 启动服务

### 方式一：直接启动 (调试用)

```bash
# 启动 NapCat
docker start napcat

# 启动 Bot
cd ~/ZZZAi
source .venv/bin/activate
python bot.py
```

### 方式二：Systemd 服务 (推荐)

#### 1. 创建 Bot 服务文件

```bash
sudo cat > /etc/systemd/system/zzzai-bot.service << 'EOF'
[Unit]
Description=ZZZAi Bot Service
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/home/你的用户名/ZZZAi
ExecStart=/home/你的用户名/ZZZAi/.venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=append:/home/你的用户名/ZZZAi/logs/bot.log
StandardError=append:/home/你的用户名/ZZZAi/logs/bot.log

[Install]
WantedBy=multi-user.target
EOF
```

#### 2. 启用服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable zzzai-bot
sudo systemctl start zzzai-bot
```

#### 3. 查看状态

```bash
sudo systemctl status zzzai-bot
sudo journalctl -u zzzai-bot -f
```

### 方式三：使用 Tmux

```bash
# 创建新会话
tmux new -s bot

# 启动 Bot
cd ~/ZZZAi
source .venv/bin/activate
python bot.py

# 分离会话: Ctrl+B, D

# 重新连接
tmux attach -t bot
```

---

## 运维管理

### 常用命令

```bash
# 查看服务状态
sudo systemctl status zzzai-bot

# 重启服务
sudo systemctl restart zzzai-bot

# 停止服务
sudo systemctl stop zzzai-bot

# 查看日志
tail -f ~/ZZZAi/logs/bot.log

# 查看 NapCat 日志
docker logs -f napcat

# 重启 NapCat
docker restart napcat
```

### 监控脚本

```bash
cat > ~/monitor.sh << 'EOF'
#!/bin/bash
echo "=== 系统资源 ==="
free -h
echo ""
echo "=== 磁盘使用 ==="
df -h /
echo ""
echo "=== Bot 状态 ==="
systemctl is-active zzzai-bot
echo ""
echo "=== NapCat 状态 ==="
docker ps | grep napcat
echo ""
echo "=== 内存占用 Top 5 ==="
ps aux --sort=-%mem | head -6
EOF

chmod +x ~/monitor.sh
./monitor.sh
```

### 自动重启脚本

```bash
cat > ~/auto_restart.sh << 'EOF'
#!/bin/bash

# 检查 Bot 是否运行
if ! systemctl is-active --quiet zzzai-bot; then
    echo "$(date) Bot 已停止，正在重启..." >> ~/logs/auto_restart.log
    sudo systemctl start zzzai-bot
fi

# 检查 NapCat 是否运行
if ! docker ps | grep -q napcat; then
    echo "$(date) NapCat 已停止，正在重启..." >> ~/logs/auto_restart.log
    docker start napcat
fi
EOF

chmod +x ~/auto_restart.sh

# 添加到 crontab (每5分钟检查)
(crontab -l 2>/dev/null; echo "*/5 * * * * ~/auto_restart.sh") | crontab -
```

### 备份脚本

```bash
cat > ~/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库和配置
tar -czf $BACKUP_DIR/zzzai_$DATE.tar.gz \
    ~/ZZZAi/data \
    ~/ZZZAi/config \
    ~/napcat/config

# 保留最近7天的备份
find $BACKUP_DIR -name "zzzai_*.tar.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_DIR/zzzai_$DATE.tar.gz"
EOF

chmod +x ~/backup.sh

# 每天凌晨3点备份
(crontab -l 2>/dev/null; echo "0 3 * * * ~/backup.sh >> ~/logs/backup.log 2>&1") | crontab -
```

---

## 常见问题

### 1. NapCat 无法连接

```bash
# 检查端口是否监听
netstat -tlnp | grep 3001

# 检查防火墙
sudo ufw status
sudo ufw allow 3001

# 检查 Docker 网络
docker network ls
docker inspect napcat | grep IPAddress
```

### 2. Bot 启动失败

```bash
# 检查 Python 版本
python --version  # 需要 3.10+

# 检查依赖
pip list

# 检查配置文件
cat config/config.yaml

# 查看详细错误
python bot.py  # 直接运行查看输出
```

### 3. 内存不足

```bash
# 查看内存使用
free -h

# 清理缓存
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# 重启服务
sudo systemctl restart zzzai-bot
docker restart napcat
```

### 4. QQ 频繁掉线

```bash
# 检查 NapCat 日志
docker logs napcat --tail 100

# 重新扫码登录
docker restart napcat
docker logs -f napcat  # 查看新二维码
```

### 5. 消息发送失败

```bash
# 检查 OneBot 连接
curl http://127.0.0.1:3001/get_login_info

# 检查 Bot 日志
tail -f ~/ZZZAi/logs/bot.log | grep -i error
```

---

## 安全建议

### 1. 防火墙配置

```bash
# 只开放必要端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow from 127.0.0.1 to any port 3001  # NapCat WS
sudo ufw enable
```

### 2. 定期更新

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 更新 Docker 镜像
docker pull mlikiowa/napcat-docker:latest
docker stop napcat
docker rm napcat
# 重新运行 docker run 命令

# 更新 Bot 依赖
cd ~/ZZZAi
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 3. 敏感信息保护

```bash
# 配置文件权限
chmod 600 config/config.yaml

# 禁止配置文件被 git 追踪
echo "config/config.yaml" >> .gitignore
```

---

## 联系支持

如遇问题，请查看：
- Bot 日志: `~/ZZZAi/logs/bot.log`
- NapCat 日志: `docker logs napcat`
- 系统日志: `journalctl -u zzzai-bot`
