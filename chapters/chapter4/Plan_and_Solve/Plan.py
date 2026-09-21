PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
最后一个步骤必须汇总历史步骤的结果，完整回答原始问题中的全部子任务。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""


PLANNER_REFLECT_PROMPT_TEMPLATE = """
你是一位严格的AI规划评审专家。请检查以下行动计划是否满足原始规划要求。

# 原始规划要求:
{task}

# 待审查的计划:
{code}

请检查：
1. 计划是否使用```python和```包围，内部是否为可由ast.literal_eval解析的非空Python字符串列表。
2. 每个步骤是否独立、可执行，顺序是否合理，是否覆盖原始问题中的全部子任务。
3. 最后一个步骤是否汇总历史步骤的结果，并完整回答原始问题。
如果全部满足，只输出“无需改进”；否则只输出具体的修改建议，不要包含“无需改进”。
"""

PLANNER_REFINE_PROMPT_TEMPLATE = """
你是一位AI规划专家。请根据评审反馈改进以下行动计划，不要编写解决问题的Python函数。

# 原始规划要求:
{task}

# 上一轮计划:
{last_code_attempt}

# 评审反馈:
{feedback}

计划必须覆盖全部子任务，按逻辑顺序排列，最后一个步骤汇总历史结果并完整回答原始问题。
只输出由```python和```包围的Python列表，每个元素都是描述可执行子任务的字符串，不要附加解释。
"""


import ast
from autogen_core import BaseAgent


def print_output_block(title: str, content: str) -> None:
    print(f"\033[34m✅ {title}---start\033[0m")
    print(content)
    print(f"\033[34m✅ {title}---end\033[0m")


class Planner:
    def __init__(self, agent: BaseAgent):
        self.agent = agent

    def plan(self, question: str) -> list[str]:
        """
        根据用户问题生成一个行动计划。
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)

        # 将规划提示词交给Agent，由Agent负责调用模型
        response_text = self.agent.run(prompt) or ""

        print_output_block("计划已生成", response_text)
        print()

        # 解析LLM输出的列表字符串
        try:
            # 找到```python和```之间的内容
            plan_str = response_text.split("```python")[1].split("```")[0].strip()
            # 使用ast.literal_eval来安全地执行字符串，将其转换为Python列表
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 解析计划时出错: {e}")
            print_output_block("大语言模型原始响应", response_text)
            return []
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误: {e}")
            return []
