# hello-agents

本项目是 [Datawhale hello-agents](https://github.com/datawhalechina/hello-agents) 教程的学习代码仓库，跟随课程逐步实现智能体（Agent）相关示例。

---

## 环境说明

### Python 版本管理 (pyenv)

项目使用 [pyenv](https://github.com/pyenv/pyenv) 管理 Python 版本，根目录下的 `.python-version` 文件指定了当前使用的 Python 版本：

```
3.10.5
```

安装对应版本后，进入项目目录时 pyenv 会自动切换：

```bash
pyenv install 3.10.5   # 如未安装该版本
cd hello-agents          # 自动激活 3.10.5
```

### 虚拟环境

项目依赖安装在虚拟环境中，虚拟环境目录已加入 `.gitignore`（不会被提交到 Git）：

| 虚拟环境目录 | 用途 |
|-------------|------|
| `.venv310/` | Python 3.10.5 对应的虚拟环境（当前使用） |

创建并激活虚拟环境：

```bash
# 创建虚拟环境（在项目根目录下）
python -m venv .venv310

# 激活虚拟环境
# Windows:
.venv310\Scripts\activate
# macOS / Linux:
source .venv310/bin/activate
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境变量配置

项目使用 `.env.json` 存放 API Key 等敏感配置（已加入 `.gitignore`），你需要自行创建该文件，格式参考：

```json
{
  "OPENAI_API_KEY": "*****",
  "OPENAI_BASE_URL": "*****",
  "TAVILY_API_KEY": "*****"
}
```

---

## 目录结构

```
hello-agents/
├── README.md                  # 项目说明（本文件）
├── .python-version            # pyenv Python 版本声明
├── .gitignore                 # Git 忽略规则
├── requirements.txt           # Python 依赖清单
└── chapters/                  # 各章节示例代码
    ├── chapter1/              # 第 1 章
    │   ├── chapter1.py        #   示例代码
    │   └── chapter1-report.md #   学习报告
    ├── chapter2/              # 第 2 章
    │   └── chapter2.py        #   示例代码
    └── chapter3/              # 第 3 章
        ├── chapter3.py        #   示例代码
        └── embedding.py       #   Embedding 向量化示例
```

### 文件说明

| 文件 | 说明 |
|------|------|
| `requirements.txt` | 项目 Python 依赖：`openai`、`requests`、`tavily-python`、`numpy`、`torch` |
| `.python-version` | pyenv 使用的 Python 版本，当前为 `3.10.5` |
| `.gitignore` | 忽略虚拟环境目录、`__pycache__`、`.env.json` 等 |
| `chapters/chapter1/chapter1.py` | 第 1 章：基础 Agent 示例 |
| `chapters/chapter2/chapter2.py` | 第 2 章：Tool Calling / 工具调用示例 |
| `chapters/chapter3/chapter3.py` | 第 3 章：RAG / 检索增强生成示例 |
| `chapters/chapter3/embedding.py` | 第 3 章配套：文本 Embedding 向量化 |

---

## 快速开始

```bash
# 1. 克隆仓库
git clone git@github.com:ykp-ykp/hello-agents.git
cd hello-agents

# 2. 确认 Python 版本
pyenv local 3.10.5

# 3. 创建并激活虚拟环境
python -m venv .venv310
# Windows
.venv310\Scripts\activate
# macOS / Linux
source .venv310/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 创建 .env.json 配置文件（填入你的 API Key）

# 6. 运行示例
python chapters/chapter1/chapter1.py
