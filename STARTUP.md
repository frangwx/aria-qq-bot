# 绝区零AI机器人 - 启动说明

## 环境要求

1. **Python环境**: Conda环境 `TraeAI`，Python 3.12+
2. **QQ NT客户端**: 从 https://im.qq.com/pcqq/index.shtml 下载安装
3. **依赖安装**: 在项目目录运行 `pip install -r requirements.txt`

## 快速启动

### 方式一：一键启动（推荐）

双击 `start.bat`，脚本会自动：
1. 启动 NoneBot2（新窗口）
2. 启动 NapCat 和 QQ

### 方式二：手动启动

**终端1 - NoneBot2:**
```cmd
cd D:\mySoft_code\ZZZAi
conda activate TraeAI
nb run
```

**终端2 - NapCat:**
```cmd
cd D:\mySoft_code\ZZZAi\napcat
launcher.bat
```

## 登录流程

1. NapCat启动后会打开QQ窗口
2. 扫码或密码登录机器人QQ账号
3. 等待NoneBot2显示：`WebSocket Connection from 127.0.0.1`
4. 向机器人QQ发送消息测试

## 机器人命令

| 命令 | 说明 | 权限 |
|------|------|------|
| `/help` | 显示帮助信息 | 所有人 |
| `/chat <消息>` | 与AI对话 | 所有人 |
| `/news` | 获取最新游戏资讯 | 所有人 |
| `/status` | 查看机器人状态 | 所有人 |
| `/refresh` | 刷新资讯缓存 | 主人 |
| `/add_keyword <关键词> <回复>` | 添加自动回复 | 主人 |
| `/del_keyword <关键词>` | 删除自动回复 | 主人 |
| `/list_keywords` | 列出所有关键词 | 主人 |

## 配置文件说明

- `config/config.yaml` - 主配置文件
- `config/sensitive_words.txt` - 敏感词过滤列表
- `config/keywords.json` - 关键词自动回复
- `napcat/config/onebot11_2745670767.json` - NapCat OneBot配置

## 常见问题

### 机器人无响应
1. 检查NoneBot2是否在8081端口运行
2. 检查NapCat WebSocket连接状态
3. 确认 `onebot11_2745670767.json` 中WebSocket URL正确

### QQ登录失败
- NapCat使用QQ NT客户端，确保是最新版本
- 尝试退出后重新扫码登录

### 端口被占用
- 检查 `.env` 文件中的 `PORT=8081`
- 终止占用端口的进程：`netstat -ano | findstr "8081"`

## 目录结构

```
ZZZAi/
├── start.bat              # 启动脚本
├── config/                # 配置文件
├── src/                   # 源代码
│   ├── llm/              # 大模型集成
│   ├── memory/           # 记忆管理
│   ├── services/         # 业务服务
│   ├── storage/          # 数据库操作
│   └── utils/            # 工具函数
├── plugins/              # NoneBot插件
│   └── zzzai.py         # 主插件
├── napcat/               # NapCat QQ协议
└── data/                 # 数据库文件
```
