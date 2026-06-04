# `chapter1.py` 执行逻辑分析报告

## 1. 文件目标

`chapter1.py` 实现了一个最小可运行的 ReAct 风格 Agent 示例：

- `LLM` 负责“思考”下一步该做什么，并输出结构化文本。
- `Agent` 主循环负责解析这段文本，决定是调用工具还是结束任务。
- 工具函数负责与外部世界交互，例如查天气、查景点。

这不是 OpenAI Function Calling 那种“模型直接返回结构化 tool call”的实现，而是一个“让模型输出文本，再由 Python 用正则解析”的手写 Agent。

## 2. 整体执行流程

程序启动后，执行顺序可以概括为：

1. 定义系统提示词 `AGENT_SYSTEM_PROMPT`，规定模型必须输出 `Thought` 和 `Action`。
2. 定义两个工具：
   - `get_weather(city)`：调用 `wttr.in` 查询天气。
   - `get_attraction(city, weather)`：调用 Tavily 搜索景点推荐。
3. 把工具注册到 `available_tools` 字典中，供 Agent 通过名字调度。
4. 初始化 `OpenAICompatibleClient`，让程序可以通过 OpenAI 兼容接口调用模型。
5. 构造初始用户请求 `user_prompt`，放进 `prompt_history`。
6. 进入最多 5 轮的主循环：
   - 把历史上下文拼成完整 prompt。
   - 调用 LLM。
   - 从 LLM 输出中解析 `Action`。
   - 如果是工具调用，就执行工具，把结果记成 `Observation`。
   - 如果是 `Finish[...]`，就结束循环并输出最终答案。

对应代码位置：

- 系统提示词：[chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:1)
- 工具定义：[chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:29)
- 工具注册：[chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:106)
- LLM 客户端：[chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:114)
- 主循环：[chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:163)

## 3. LLM 与 Agent 的交互机制

这里的核心不是“模型会不会回答”，而是“模型如何被约束成一个可被程序驱动的决策器”。

### 3.1 system prompt 先定义协议

在 [chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:1) 中，`AGENT_SYSTEM_PROMPT` 明确规定了：

- 可用工具有哪些。
- 每次只能输出一对 `Thought` 和 `Action`。
- `Action` 只能是两种之一：
  - `function_name(arg_name="arg_value")`
  - `Finish[最终答案]`

这一步很关键，因为后面的 Agent 并不理解自然语言语义，它只会按固定格式解析文本。也就是说：

- `LLM` 负责生成“符合协议的下一步动作”
- `Agent` 负责“按协议执行动作”

两者之间的接口，本质上就是一段受 prompt 约束的文本。

### 3.2 Agent 把历史轨迹作为上下文喂回给 LLM

在 [chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:158) 和 [chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:168)：

- 初始时，`prompt_history = [f"用户请求: {user_prompt}"]`
- 每一轮把 `prompt_history` 用换行拼成 `full_prompt`

这意味着 LLM 每次看到的不是单独一句用户问题，而是完整轨迹，例如：

```text
用户请求: ...
Thought: ...
Action: get_weather(city="北京")
Observation: 北京当前天气：Patchy rain nearby，气温19摄氏度
```

这种设计让模型具备“短期工作记忆”：

- 它知道自己上一轮做了什么。
- 它知道工具返回了什么。
- 它可以基于新的 `Observation` 决定下一步动作。

所以这段代码里，真正驱动多步推理的不是 Python 本身，而是：

`prompt_history` 持续累积出的“可见行动历史”。

### 3.3 LLM 只负责决策，不直接执行工具

在 [chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:170-171)，主循环调用：

```python
llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
```

`generate()` 内部只是把两条消息发给模型：

- `system`: 协议与规则
- `user`: 当前完整轨迹

对应代码在 [chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:126-134)。

LLM 返回的是普通文本，例如实际运行中第一轮返回：

```text
Thought: 用户想了解北京的天气，并根据天气推荐合适的旅游景点。我需要先查询北京的天气。
Action: get_weather(city="北京")
```

注意这里的 `Action` 只是“建议执行什么”，真正执行工具的是 Agent，不是 LLM。

### 3.4 Agent 通过正则把文本动作转成真实调用

这部分是整个 Agent 的执行核心，在 [chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:183-203)。

执行步骤是：

1. 用正则找出 `Action: ...`
2. 判断是否以 `Finish` 开头
3. 如果不是 `Finish`，继续解析：
   - 工具名：`re.search(r"(\w+)\(", action_str).group(1)`
   - 参数串：`re.search(r"\((.*)\)", action_str).group(1)`
   - 键值参数：`re.findall(r'(\w+)="([^"]*)"', args_str)`
4. 从 `available_tools` 里取出同名函数并执行

也就是说，这里有一条很清晰的责任边界：

- `LLM` 输出：`get_weather(city="北京")`
- `Agent` 翻译成：`available_tools["get_weather"](city="北京")`

这就是 LLM 与 Agent 的真正交互点。

### 3.5 工具结果再回流给 LLM

工具执行完后，在 [chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:206-209)：

```python
observation_str = f"Observation: {observation}"
prompt_history.append(observation_str)
```

这一步把真实世界返回的信息重新写回上下文，形成闭环：

1. `LLM` 规划动作
2. `Agent` 执行动作
3. 工具产生结果
4. `Agent` 把结果写成 `Observation`
5. `LLM` 读取 `Observation` 后规划下一步

这就是一个完整的 ReAct 循环。

## 4. 实际运行时的三轮交互

这次运行中，程序实际经历了 3 轮：

### 第 1 轮

- 输入给 LLM：只有用户请求
- LLM 输出：先查北京天气
- Agent 执行：`get_weather(city="北京")`
- Observation：`北京当前天气：Patchy rain nearby，气温19摄氏度`

### 第 2 轮

- 输入给 LLM：用户请求 + 上一轮 Thought/Action + 天气 Observation
- LLM 输出：根据“局部有雨”去查合适景点
- Agent 执行：`get_attraction(city="北京", weather="Patchy rain nearby")`
- Observation：Tavily 返回室内景点推荐

### 第 3 轮

- 输入给 LLM：前两轮的完整轨迹
- LLM 判断信息已足够
- 输出：`Finish[...]`
- Agent 解析 `Finish`，结束循环

这个过程非常能说明该代码的设计意图：

- `LLM` 不保存程序状态
- 状态由 `prompt_history` 维护
- `Agent` 是调度器
- 工具是外部能力

## 5. 从代码结构看，谁在扮演“Agent”

严格说，这个文件里没有单独定义一个 `Agent` 类，但“Agent 行为”是存在的，主要由主循环承担：

- 维护上下文：`prompt_history`
- 调用模型：`llm.generate(...)`
- 解析动作：正则提取 `Action`
- 路由工具：`available_tools[tool_name](**kwargs)`
- 写回观察：`prompt_history.append(observation_str)`
- 判断终止：`Finish[...]`

所以可以把 [chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:163) 开始的 `for` 循环理解成这个示例里的 Agent runtime。

## 6. 这种交互方式的优点

### 6.1 好理解

代码把 Agent 的关键机制全部摊开了：

- prompt 怎么组织
- 工具怎么注册
- 动作怎么解析
- 观察怎么反馈给模型

很适合教学或入门理解。

### 6.2 容易扩展更多工具

如果要加新工具，只需要：

1. 写函数
2. 放进 `available_tools`
3. 在 system prompt 里告诉模型这个工具存在

### 6.3 清楚展示 ReAct 思路

这段代码完整体现了：

- Reason：`Thought`
- Act：`Action`
- Observe：`Observation`

这是典型的 ReAct Agent 最小骨架。

## 7. 这种实现的局限与风险

虽然示例清晰，但它也很脆弱，脆弱点基本都出在“LLM 与 Agent 之间靠自由文本协议通信”。

### 7.1 对输出格式强依赖

如果模型没有严格输出：

```text
Thought: ...
Action: ...
```

解析就可能失败。代码里虽然做了兜底：

- 如果解析不到 `Action`，就写回一个错误 Observation 让模型重试

但整体仍然依赖模型守规矩。

### 7.2 参数解析能力很弱

参数只支持这种形式：

```text
tool_name(arg="value")
```

对应正则在 [chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:197-199)。

这意味着它对以下情况都不稳：

- 参数里含引号
- 参数里含逗号
- 多行参数
- 非字符串参数
- 嵌套结构参数

### 7.3 工具调用缺少强约束

Agent 只是从字符串里提取函数名，再去 `available_tools` 里查。优点是简单，缺点是：

- 没有 schema 校验
- 没有参数类型校验
- 没有更细的权限控制

相比现代函数调用接口，这种方式更容易被格式波动击穿。

### 7.4 密钥硬编码

在 [chapter1.py](D:\study\Python-Projects\hello-agents\chapter1.py:146-149) 里，`API_KEY` 和 `TAVILY_API_KEY` 被直接写进源码。

这和 LLM-Agent 交互机制无关，但属于执行层面的明显风险：

- 不利于分享代码
- 容易泄漏凭证
- 不利于环境切换

## 8. 可以怎样理解这段代码里的角色分工

如果用一句话概括：

- `LLM` 是“文本决策器”
- 主循环是“Agent 调度器”
- `available_tools` 是“能力注册表”
- `Observation` 是“工具执行结果回写机制”

更具体一点：

- LLM 决定下一步“应该做什么”
- Agent 决定这一步“怎么被执行”
- 工具负责“真正去拿外部信息”
- 历史上下文负责“把过去发生过的事情告诉 LLM”

## 9. 结论

`chapter1.py` 的本质是一个“基于文本协议的最小 Agent 框架”：

- 它先用 `system prompt` 约束模型输出动作格式。
- 再由主循环把模型输出解析为真实函数调用。
- 工具执行结果以 `Observation` 的形式返回给模型。
- 模型据此继续决策，直到输出 `Finish[...]`。

如果你的关注点是“LLM 如何与 agent 交互”，这段代码最关键的不是模型本身，而是这条闭环：

`system prompt 定义协议 -> LLM 输出 Action -> Agent 解析并执行 -> Observation 回写 -> LLM 继续决策`

这就是整份代码的核心执行逻辑。

## 10. 本次验证结果

我实际运行了脚本，观察到的真实路径与源码分析一致：

1. 第 1 轮调用 `get_weather(city="北京")`
2. 第 2 轮调用 `get_attraction(city="北京", weather="Patchy rain nearby")`
3. 第 3 轮输出 `Finish[...]` 并结束

说明这份代码当前确实是按一个三步 ReAct Agent 在工作。
