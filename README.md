# EcomAgent | 电商 Agent 实战工坊

从零到一构建面向电商客服场景的企业级 AI Agent 系统。

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- API Key（支持任意 OpenAI 兼容接口）

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/<your-username>/EcomAgent.git
cd EcomAgent

# 2. （推荐）创建虚拟环境
python -m venv ecom
# Windows
ecom\Scripts\activate
# macOS / Linux
source ecom/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 配置

复制环境变量模板并编辑：

```bash
cp .env.example .env
```

修改 `.env`，填入你的 API 密钥和地址：

```ini
# === 必填 ===
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-5.5
TEMPERATURE=0.7

# === Embedding（默认复用 LLM 配置，无需额外填写） ===
EMBEDDING_MODEL=text-embedding-3-small

> 💡 如果你使用的 API 中转站不支持 embedding 模型，可在构建索引时加 `--local-embed` 参数，使用 Chroma 内置的本地模型（all-MiniLM-L6-v2，纯离线，无需 API）。
```

> 💡 中转站兼容 OpenAI API，LLM 与 Embedding 共用同一地址。`EMBEDDING_API_KEY` 和 `EMBEDDING_BASE_URL` 留空即可。
> 若不支持 embedding 模型，构建索引时加 `--local-embed` 使用本地模型（all-MiniLM-L6-v2，纯离线）。

```ini
# === MCP 集成（第4期） ===
MCP_ENABLED=false                  # 是否启用 MCP
MCP_SERVER_URL=http://127.0.0.1:9123/mcp

# === Multi-Agent 模式（第6期） ===
MULTI_AGENT_ENABLED=false          # 是否启用多 Agent 协作

# === Memory 记忆系统（第7期） ===
MEMORY_ENABLED=true                # 是否启用记忆
MEMORY_USER_ID=default             # 当前用户 ID
MAX_LTM_FACTS=50                   # 长期记忆最大事实数

# === Skill 技能模块（第8期） ===
SKILLS_ENABLED=true                # 是否启用 Skill
SKILLS_DIR=app/agent/skills/definitions

# === RAG 知识库检索（第5期） ===
RAG_BACKEND=numpy                  # 向量后端：numpy | chroma
KB_DIR=app/agent/rag/knowledge     # 知识库源文档目录
```

> 💡 所有配置项均有默认值，使用同一服务商时只需填写 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`MODEL_NAME` 三项即可启动。

### 构建知识库索引（首次运行前必须执行）

```bash
# 使用 NumPy 后端（默认，教学用，零依赖）
python app/scripts/build_kb_index.py --backend numpy

# 或使用 ChromaDB 后端（生产级向量数据库）
python app/scripts/build_kb_index.py --backend chroma

# 若 API 中转站不支持 embedding 模型，可用 Chroma 内置的本地模型（纯离线，无需 API）
python app/scripts/build_kb_index.py --backend chroma --local-embed
```

### 启动主程序

```bash
python main.py
```

启动后进入交互式 CLI，客服 AI 名叫 **"小夕"**。支持以下命令：

| 命令 | 功能 |
|------|------|
| 直接输入文本 | 与客服对话 |
| `quit` / `exit` | 退出程序（自动保存记忆） |
| `reset` | 重置当前对话（清空历史并持久化记忆） |
| `memory` | 查看短期记忆和长期记忆内容 |
| `skills` | 查看当前可用的技能列表 |

> 默认运行在**单 Agent 模式**。如需 Multi-Agent 模式，设置 `.env` 中 `MULTI_AGENT_ENABLED=true` 后重新启动。

### 启动 Web 界面（Gradio）

```bash
python app/gradio_app.py
```

浏览器打开 **http://127.0.0.1:7860** 即可在网页中与小夕对话，支持意图识别、置信度展示等结构化信息显示。

### 启动 MCP Server（独立工具服务）

```bash
python mcp_server/server.py
```

默认监听 `http://127.0.0.1:9123/mcp`，主程序设置 `MCP_ENABLED=true` 后自动连接使用 MCP 工具。MCP Server 为独立微服务，电商工具（查订单、查商品、查物流、申请退款、知识检索）以标准协议暴露，可被任何 MCP 客户端调用。

#### 💬 对话测试示例

启动后可直接输入以下内容与小夕对话：

<details>
<summary><b>📦 查订单</b></summary>

```
帮我查一下 ORD-20240115-001 这个订单
查订单 ORD-20240110-003
我的订单 ORD-20240122-005 发货了没有
```
</details>

<details>
<summary><b>🚚 查物流</b></summary>

```
ORD-20240115-001 的物流到哪了
追踪一下 SF1234567890
```
</details>

<details>
<summary><b>🔍 查商品</b></summary>

```
有没有 Nike 运动鞋
AirPods Pro 2 多少钱
戴森吸尘器还有货吗
```
</details>

<details>
<summary><b>↩️ 申请退款</b></summary>

```
我要退款 ORD-20240120-002，不想要了
ORD-20240118-004 退款到哪一步了
```
</details>

<details>
<summary><b>📖 咨询政策（知识库检索）</b></summary>

```
退换货几天内有效
配送一般多久到
会员有什么权益
怎么申请退款
```
</details>

<details>
<summary><b>💬 闲聊</b></summary>

```
你好
你是谁
```
</details>

### 启动 MCP Server（独立微服务）

```bash
python mcp_server/server.py
```

默认监听 `http://127.0.0.1:9123/mcp`，通过 Streamable HTTP 暴露电商工具（查订单、查商品、查物流、申请退款、知识检索）。

主程序需设置 `MCP_ENABLED=true` 来连接使用 MCP 工具。

> **注：** MCP（Model Context Protocol）是 Anthropic 推出的开放协议，旨在统一 LLM 应用与外部工具的调用标准。本项目的 MCP Server 将电商工具封装为独立微服务，与主 Agent 通过 Streamable HTTP 通信。这样做的好处是：
>
> 1. **解耦** — 未来电商后端切换为真实 API 时，只需修改 MCP Server 内部实现，主 Agent 代码无需改动。
> 2. **复用** — 任何支持 MCP 协议的客户端（Claude Desktop、VS Code、自定义 Agent）均可连接此服务，不局限于本项目的 Agent。
> 3. **面试亮点** — MCP 是目前 Agent 领域的前沿协议，项目中体现 MCP 集成能让简历更有竞争力。

### 运行测试

```bash
pytest tests/ -v
```

### 运行评估

```bash
# 单 Agent 模式评估
python app/scripts/run_eval.py --mode single

# Multi-Agent 模式评估
python app/scripts/run_eval.py --mode multi

# 带 LLM-as-judge 评估
python app/scripts/run_eval.py --judge

# 指定输出文件
python app/scripts/run_eval.py --output report.json
```

---

## 📖 项目背景

大家好，我是**淮南**，Top 985 科班出身，有多家大厂后端 & AI Agent 研发经验。

我在小红书上运营着一个 **AI Agent 面经系列**，分享了我面试字节、阿里、MiniMax 等多家公司 AI Agent 岗位的真实面经，目前已经积累了 5000+ 粉丝。在和大家交流的过程中，我发现很多同学对 Agent 相关技术很感兴趣，但苦于没有一个**完整的、可跟着动手的实战项目**。

所以我决定做这件事 —— **以电商客服为场景，从零到一带大家实战一个企业级 Agent 系统**。

### 为什么选电商客服？

电商客服是 Agent 最经典的落地场景之一：业务逻辑清晰（查订单、退换货、推荐商品、售后处理），大家容易理解，面试中也经常被问到。做完这个项目，你不仅能掌握 Agent 核心技术栈，还能直接写进简历。

### 更新方式

我会在小红书上**每期更新一个 Agent 相关技术**，对应本仓库的一个 commit / tag。特别复杂的技术点会拆成 2 期。你可以跟着每期笔记，checkout 到对应的 tag，一步一步跟着做。

> 扫码关注我的小红书，获取每期更新通知：

<p align="center">
  <img src="./淮南-小红书.jpg" alt="淮南-小红书" width="300" />
</p>

---
