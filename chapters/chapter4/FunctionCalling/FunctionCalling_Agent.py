import json
import os
import sys

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, ".."))

from llm_client import HelloAgentsLLM


def get_order_status(order_id: str) -> str:
    """
    一个本地业务函数，用来模拟真实系统查询。
    """
    orders = {
        "A100": "订单A100已发货，快递单号为 SF123456。",
        "B200": "订单B200正在仓库拣货，预计今天发出。",
        "C300": "订单C300已取消。",
    }
    return orders.get(order_id, f"没有找到订单 {order_id}。")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "根据订单号查询订单状态。",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "订单号，例如 A100、B200、C300。",
                    }
                },
                "required": ["order_id"],
            },
        },
    }
]


class FunctionCallingAgent:
    """
    Function Calling 范式的最小示例。

    关键区别：
    - ReAct 让模型用文本写出 Action，再由 Agent 解析文本。
    - Function Calling 让模型输出结构化 tool_calls，Agent 直接按函数名和参数执行。
    """

    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
        self.functions = {"get_order_status": get_order_status}

    def run(self, question: str) -> str:
        messages = [
            {
                "role": "system",
                "content": "你是一个订单助手。需要查询订单时，请调用可用函数，不要自己编造订单状态。",
            },
            {"role": "user", "content": question},
        ]

        print(f"\n--- 用户问题 ---\n{question}")
        print("\n--- 第一次调用模型：让模型决定是否调用函数 ---")
        first_response = self.llm_client.client.chat.completions.create(
            model=self.llm_client.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0,
        )
        print(first_response.model_dump_json(indent=2))
        assistant_message = first_response.choices[0].message
        messages.append(assistant_message.model_dump(exclude_none=True))

        if not assistant_message.tool_calls:
            answer = assistant_message.content or ""
            print(f"\n--- 模型直接回答 ---\n{answer}")
            return answer

        print("\n--- Agent 执行模型请求的函数 ---")
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_result = self.functions[function_name](**function_args)

            print(f"函数名: {function_name}")
            print(f"参数: {function_args}")
            print(f"结果: {function_result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": function_result,
                }
            )

        print("\n--- 第二次调用模型：让模型基于函数结果回答用户 ---")
        final_response = self.llm_client.client.chat.completions.create(
            model=self.llm_client.model,
            messages=messages,
            temperature=0,
        )
        print(final_response.model_dump_json(indent=2))
        final_answer = final_response.choices[0].message.content or ""

        print(f"\n--- 最终答案 ---\n{final_answer}")
        return final_answer


if __name__ == "__main__":
    try:
        llm_client = HelloAgentsLLM()
        agent = FunctionCallingAgent(llm_client)
        agent.run("请帮我查询订单A100现在是什么状态，并用一句话回复用户。")
    except ValueError as e:
        print(e)
