---
name: project-startup-analyzer
description: 分析项目结构并生成启动/配置文档。读取项目关键配置文件，梳理依赖、环境要求、启动命令，输出完整的 README 或启动指南。适用场景：用户问"如何启动这个项目"、"项目怎么配置"、"写个 README"。
---

## 项目启动分析流程

当用户想了解如何启动项目，或要求写 README 时，按以下流程处理。

### 第一步：扫描项目结构

按优先级读取以下配置文件（存在即读）：

1. **Python 项目**：
   - `pyproject.toml` → 依赖、Python 版本、脚本入口
   - `requirements.txt` → 依赖列表
   - `setup.py` / `setup.cfg` → 包配置
   - `.env.example` → 环境变量模板

2. **Java/Spring 项目**：
   - `pom.xml` → Maven 依赖、模块结构
   - `build.gradle` → Gradle 配置
   - `application.yml` / `application.properties` → 应用配置

3. **通用**：
   - `docker-compose.yml` / `docker-compose.*.yml` → 容器编排
   - `Dockerfile` → 镜像构建
   - `Makefile` → 常用命令
   - `README.md` → 现有文档

### 第二步：提取关键信息

从配置文件中提取：

- **语言/框架**：Python 3.x、Java 17、Spring Boot 3.x 等
- **依赖服务**：MySQL、Redis、Neo4j、RabbitMQ 等及版本要求
- **环境变量**：必填项（API Key、数据库连接等）
- **启动命令**：安装依赖、构建、运行的具体命令
- **端口占用**：服务监听的端口号

### 第三步：生成启动文档

输出结构：

```markdown
# [项目名]

> 一句话描述项目用途

## 技术栈

- 语言：xxx
- 框架：xxx
- 依赖服务：xxx

## 快速启动

### 1. 环境准备

[安装必要工具的命令]

### 2. 安装依赖

[依赖安装命令]

### 3. 配置环境变量

cp .env.example .env
# 编辑 .env 填写必要配置

### 4. 启动服务

[按顺序启动的命令]

### 5. 验证

[验证服务正常运行的方法]

## 常用命令

| 命令 | 说明 |
|------|------|
| xxx | xxx |
```

### 注意事项

- 如果项目已有 README，先读取再补充/修正，不要重写
- 标注哪些环境变量是必填的，哪些有默认值
- 如果有多个启动方式（本地/Docker），都列出
- 如果发现配置缺失或矛盾，主动指出并给出建议
