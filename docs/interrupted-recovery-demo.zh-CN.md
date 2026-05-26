# 中断恢复演示

这个演示只说明一件事：

```text
AI 干活中断以后，下一次回来能知道做到哪了、产物在哪、下一步该干什么。
```

它不需要后台服务，不需要外部账号，也不需要任何外部通信工具或云服务。

## 没有 Watchtower 时

常见情况是这样的：

```text
AI 刚才在干活。
终端关了，窗口没了，或者会话断了。
下一次再打开，AI 不知道上一段做到哪。
人还得重新解释一遍。
```

这就是“断片”。

## 有 Watchtower 后

Watchtower 会在本地留下一个很小的工作交接本：

- 当前目标是什么。
- 下一个安全动作是什么。
- 上一次做完的小步骤是什么。
- 最新产物文件在哪。

所以新窗口或新 Agent 醒来以后，不用先猜，也不用立刻让人重新讲一遍。

## 本地快速跑一遍

安装后运行：

```bash
ROOT="$(mktemp -d)"
agent-watchtower --root "$ROOT" init
agent-watchtower --root "$ROOT" worker-status
agent-watchtower --root "$ROOT" worker-run --result "记录真实工作结果，并验证 artifact path。"
agent-watchtower --root "$ROOT" artifact-path
```

如果你在源码目录里，也可以运行：

```bash
./scripts/demo_interrupted_recovery.sh
```

你会看到：

- `init` 创建一个演示目标和一个待办小任务。
- `worker-status` 告诉你现在有没有任务能继续做。
- `worker-run --result ...` 记录真实工作结果，并写出一份 markdown 产物。
- `artifact-path` 告诉你最新产物在哪里。

## 关掉再回来

关掉终端，再打开一个新终端，只要还用同一个 `ROOT`：

```bash
agent-watchtower --root "$ROOT" worker-status
agent-watchtower --root "$ROOT" artifact-path
```

Agent 就能看见本地记录，然后用普通话解释：

```text
我查到了本地 Watchtower 状态。上一段做完了哪个小步骤、产物在哪、下一步应该怎么做，都有记录。我可以从这里继续，不需要你从头再讲。
```

## 这个演示证明什么

它证明第一阶段的价值：

```text
不是让 AI 永远自动干活。
而是让 AI 停下来以后，再醒来不从零开始。
```

后续如果要做更强的自适应节奏、自动唤醒、多工具协作，那是下一阶段。v0 先把“不断片、能接上”这件事做扎实。
