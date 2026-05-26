# Agent Watchtower Core

**语言：** [English](README.md) | 简体中文

**给 AI 编程助手用的本地工作交接本。**

你让 Codex、Claude Code、Hermes、CodeWhale 或其他编程 Agent 干活。它写了一会代码，终端关了、会话断了、上下文太长了，或者你第二天回来换了一个窗口。

问题就来了：

- 它到底做到哪了？
- 下一步原本要做什么？
- 有用的产物放哪了？
- 换一个 Agent 能不能接着干？

Agent Watchtower 解决的是这个第一阶段问题：**醒来以后不从零开始。**

它不是新的 AI，也不是后台常驻服务。它只是一个很小的本地 CLI，把关键状态写成普通文件，让下一次会话能接着看。

## 快速跑通本地演示

安装后运行：

```bash
ROOT="$(mktemp -d)"
agent-watchtower --root "$ROOT" init
agent-watchtower --root "$ROOT" worker-status
agent-watchtower --root "$ROOT" worker-run --result "创建了第一份交接记录，并验证了本地 receipt。"
agent-watchtower --root "$ROOT" artifact-path
```

你会看到：

- `worker-status`：现在有没有可以继续做的小任务。
- `worker-run --result ...`：把真实工作结果写进产物，并写一份记录。
- `artifact-path`：告诉你最新产物在哪。

关掉终端再回来，这些本地记录还在。

想看更直白的“断片前 / 断片后”对比，见：

```text
docs/interrupted-recovery-demo.zh-CN.md
```

源码目录里也可以直接跑：

```bash
./scripts/demo_interrupted_recovery.sh
```

## 安装方式

官网：

- 英文：http://www.adgwmuren.top/
- 中文：http://www.adgwmuren.top/zh-CN.html

HTTPS 证书还在 GitHub Pages 签发中，目前先用 HTTP。

## 支持哪些系统

Agent Watchtower 是普通 Python 命令行工具，只在本地写 JSON 和 markdown 文件。

- macOS：当前发布流程已实测。
- Linux：支持目标，需要 Python 3.11 或更新版本。
- Windows：支持目标，需要 Python 3.11 或更新版本；推荐用 `pip`、`pipx` 或 `uv`，不要用 Homebrew。

从 PyPI 安装：

```bash
python3 -m pip install agent-watchtower-core
```

用 Homebrew 安装：

```bash
brew tap un-n-smith/tap
brew install agent-watchtower
```

从 GitHub 安装：

```bash
python3 -m pip install "agent-watchtower-core @ git+https://github.com/un-n-smith/agent-watchtower.git"
```

如果你常装命令行工具，也可以用 `pipx` 隔离安装：

```bash
pipx install agent-watchtower-core
```

或者用 `uv`：

```bash
uv tool install agent-watchtower-core
```

从本地源码目录安装：

```bash
python3 -m pip install .
```

查看版本：

```bash
agent-watchtower --version
```

## 用在真实项目里

建议用项目本地目录保存状态：

```bash
agent-watchtower --root .watchtower init
agent-watchtower --root .watchtower task-add \
  --title "检查仓库状态" \
  --next-action "运行 git status 并总结待处理变化" \
  --done-definition "产物写清楚变化文件和下一步安全动作"
```

做完真实工作后，把结果写进去：

```bash
agent-watchtower --root .watchtower worker-run \
  --result "已运行 git status。发现 README.md 有文档修改，没有源码修改。"
agent-watchtower --root .watchtower artifact-path
```

如果 Agent 需要更严格的机器指令，可以看：

```text
AGENTS.structured.md
```

## 它和 TODO.md 有什么区别

TODO 文件当然有用，但每个 Agent 都要猜格式。Watchtower 固定了三件事：

- 固定的本地文件结构。
- 固定的 5 个 CLI 命令。
- 把“做过什么”“结果在哪”“下一步安全动作是什么”分开记录。

## 它会保存什么

默认保存到：

```text
~/.agent-watchtower
```

里面是普通本地文件：

- `goals.json`：当前目标。
- `work-queue.json`：下一步小任务。
- `run-receipts.json`：刚才做过什么。
- `work-artifacts/*.md`：产物和说明。

## 公开命令

第一版只有 5 个命令：

```text
init
task-add
worker-status
worker-run
artifact-path
```

## 它不是什么

它不是完整记忆系统。  
它不是自动工作机器人。  
它不会自己创建账号、发钱、发云资源、回复客户。  
它不替你做商业、法律、账号、发布权限这些决定。

它只做一件小事：

**让 Agent 停下来以后，下次醒来知道从哪里继续。**

## 反馈

如果它帮你的 Agent 从中断里恢复了，或者没恢复成功，欢迎开 issue 告诉我们。

最好附上：

- 你用的 Agent。
- 操作系统和 Python 版本。
- 你跑过的命令。
- `artifact-path` 输出。
- 下一次会话是否真的能接着干。

真实用户的问题、失败场景、改进建议，是这个项目继续变好的动力。
