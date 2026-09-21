from abc import ABC, abstractmethod
from typing import Optional

from llm_client import HelloAgentsLLM


class BaseAgent(ABC):
    """
    所有 Agent 范式的抽象基类。

    约定的最小范式：
    - 构造时持有一个 LLM 客户端 (llm_client)
    - 实现 run(question) 方法，接收用户问题并返回最终答案

    不同的 Agent 范式（ReAct / Function Calling / Plan-and-Solve 等）
    只需继承本类并实现 run 方法，即可获得统一的调用接口。
    """

    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client

    @abstractmethod
    def run(self, question: str) -> Optional[str]:
        """
        运行 Agent，处理用户问题并返回最终答案。

        Args:
            question: 用户输入的问题。

        Returns:
            Agent 的最终答案；若流程未能正常完成，可返回 None。
        """
        raise NotImplementedError


if __name__ == "__main__":
    # 演示：BaseAgent 不能被直接实例化
    try:
        BaseAgent(HelloAgentsLLM())
    except TypeError as e:
        print(f"✅ 抽象类校验通过: {e}")

