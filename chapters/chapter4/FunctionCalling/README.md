# Function Calling

Function Calling 的核心思想是：模型不再用普通文本描述要调用哪个工具，而是输出结构化的 `tool_calls`，由 Agent 根据函数名和参数去执行本地函数，再把函数结果交回模型生成最终回答。

## 和 ReAct 的区别

ReAct 常见流程是：

```text
Thought -> Action(文本) -> Agent解析Action -> Observation -> Thought...
```

Function Calling 常见流程是：

```text
用户问题 -> 模型输出tool_calls -> Agent执行本地函数 -> 模型基于函数结果回答
```

所以它的重点不是设计 `Thought/Action/Observation` 的文本格式，而是把可用函数声明成结构化 schema，让模型在需要时选择函数并填好参数。

## 运行

```powershell
python .\chapters\chapter4\FunctionCalling\FunctionCalling_Agent.py
```

示例里只有一个本地函数 `get_order_status(order_id)`，用于模拟查询订单状态。
