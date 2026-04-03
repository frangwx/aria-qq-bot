# Aria QQ Bot

<div align="center">

**aria QQ bot**

基于 NoneBot2 开发的智能对话机器人，AI练手小项目

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![NoneBot2](https://img.shields.io/badge/NoneBot2-2.0+-green.svg)](https://nonebot.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 功能特性

- **智能对话** - 集成 OpenAI API，支持上下文记忆和多轮对话
- **资讯推送** - 自动爬取米游社公告、活动、资讯，定时推送
- **关键词触发** - 自定义关键词自动回复，支持正则匹配
- **会话管理** - 短期记忆 + 长期向量存储，记住用户偏好
- **权限系统** - 多级权限管理，支持主人/管理员/普通用户
- **敏感词过滤** - 内置敏感词检测，保障对话安全

## 快速开始

### 环境要求

- Python 3.10+
- NapCat (QQ协议端)
- OpenAI API Key (或其他兼容 API)

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/10924/aria-QQ-bot.git
cd aria-QQ-bot
```

#### 2. 创建虚拟环境

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置文件

```bash
# 复制配置模板
cp config/config.example.yaml config/config.yaml

# 编辑配置文件
vim config/config.yaml
```

配置说明：

```yaml
# Bot 基础配置
bot:
  name: "Aria"
  superusers:
    - "你的QQ号"  # 主管理员QQ号

# LLM 配置
llm:
  provider: "openai"
  api_key: "你的API密钥"  # OpenAI API Key
  base_url: "https://api.openai.com/v1"  # 可替换为兼容API
  model: "gpt-4o-mini"  # 模型名称

# 存储配置
storage:
  database: "./data/aria.db"
  vector_path: "./data/memory/"

# NapCat 连接配置
adapter:
  onebot:
    ws_urls:
      - "ws://127.0.0.1:3001"  # NapCat WebSocket 地址
```

### NapCat 安装

NapCat 是 QQ 协议端，用于接收和发送 QQ 消息。

#### Docker 部署 (推荐)

```bash
# 拉取镜像
docker pull mlikiowa/napcat-docker:latest

# 创建数据目录
mkdir -p ~/napcat/data ~/napcat/config

# 启动容器
docker run -d \
  --name napcat \
  --restart=always \
  -p 3001:3001 \
  -p 6099:6099 \
  -v ~/napcat/data:/app/.config/QQ \
  -v ~/napcat/config:/app/napcat/config \
  mlikiowa/napcat-docker:latest

# 查看二维码扫码登录
docker logs -f napcat
```

#### 配置 NapCat

创建 `~/napcat/config/onebot11.json`：

```json
{
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
  }
}
```

### 启动 Bot

#### Windows

```bash
# 双击运行
start.bat

# 或命令行运行
python bot.py
```

#### Linux

```bash
# 直接运行
python bot.py

# 后台运行
nohup python bot.py > logs/bot.log 2>&1 &

# 使用 systemd (推荐)
sudo systemctl start zzzai-bot
```

## 使用说明

### 基础命令

| 命令 | 说明 | 权限 |
|------|------|------|
| `#帮助` | 查看帮助信息 | 所有人 |
| `#状态` | 查看 Bot 状态 | 所有人 |
| `#清除记忆` | 清除当前会话记忆 | 所有人 |
| `#刷新资讯` | 手动刷新资讯 | 管理员 |
| `#推送资讯` | 推送未读资讯 | 管理员 |
| `#设置主人 @用户` | 添加主人权限 | 主人 |

### 对话功能

直接发送消息即可与 Bot 对话：

```
用户: 今天有什么活动？
Aria: 今天有「灾潮特遣分队」活动，参与可以获得...
```

### 关键词触发

在 `data/keywords.json` 中配置：

```json
[
  {
    "keyword": "攻略",
    "reply": "请查看最新攻略：https://example.com/guide",
    "is_regex": false
  },
  {
    "keyword": "版本.*更新",
    "reply": "新版本内容已发布，请查看公告",
    "is_regex": true
  }
]
```

## 项目结构

```
aria-QQ-bot/
├── bot.py                 # 入口文件
├── plugins/
│   └── zzzai.py          # 主插件
├── src/
│   ├── llm/              # LLM 集成
│   │   ├── provider.py   # 提供者基类
│   │   └── openai_provider.py
│   ├── services/         # 业务服务
│   │   ├── chat/         # 对话服务
│   │   ├── news/         # 资讯服务
│   │   ├── game/         # 游戏数据
│   │   └── push/         # 推送服务
│   ├── storage/          # 数据存储
│   │   └── database.py
│   ├── memory/           # 记忆管理
│   └── utils/            # 工具函数
├── config/
│   └── config.example.yaml
├── data/                  # 数据目录
├── logs/                  # 日志目录
├── requirements.txt
├── DEPLOY.md             # 详细部署文档
└── README.md
```

## 部署到服务器

详细部署说明请查看 [DEPLOY.md](DEPLOY.md)

### 快速部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置
cp config/config.example.yaml config/config.yaml
vim config/config.yaml

# 3. 启动 NapCat (Docker)
docker run -d --name napcat -p 3001:3001 mlikiowa/napcat-docker:latest

# 4. 启动 Bot
python bot.py
```

## 常见问题

### Q: Bot 无法连接 NapCat

检查 NapCat 是否正常运行：

```bash
docker logs napcat
```

确认 WebSocket 端口配置正确。

### Q: 对话无响应

1. 检查 API Key 是否正确
2. 检查网络是否能访问 API
3. 查看日志 `logs/bot.log`

### Q: 资讯刷新失败

米游社 API 可能更新，检查 `src/services/news/crawler.py` 中的 API 地址。

## 技术栈

- **框架**: [NoneBot2](https://nonebot.dev/)
- **协议**: [OneBot V11](https://onebot.dev/) + [NapCat](https://napneko.github.io/)
- **LLM**: OpenAI API (兼容各种后端)
- **数据库**: SQLite + SQLAlchemy
- **向量存储**: ChromaDB

## 开发计划

- [ ] 支持更多 LLM 后端 (Claude, Gemini)
- [ ] 添加游戏数据查询 (角色、武器)
- [ ] 群聊管理功能
- [ ] Web 管理后台
- [ ] 多语言支持

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE)

---

<div align="center">

**Made with ❤️ for Zenless Zone Zero**

</div>
# aria-qq-bot
# aria-qq-bot
