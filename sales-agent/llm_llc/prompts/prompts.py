from enum import Enum
import json


folder = "kb/prompts/"


class PromptTypes(Enum):
    SALES_AGENT_TOOLS_PROMPT = (1, "SALES_AGENT_TOOLS_PROMPT.txt")
    SALES_AGENT_CONVERSATION_PROMPT = (2, "SALES_AGENT_CONVERSATION_PROMPT.txt")
    STAGE_ANALYZER_PROMPT = (3, "STAGE_ANALYZER_PROMPT.txt")

    def __init__(self, id, filename):
        self.id = id
        self.filename = filename


class Prompts:
    @classmethod
    def get_prompt(cls, prompt_type: PromptTypes) -> str:
        with open(folder + prompt_type.filename, "r") as f:
            return f.read()


if __name__ == "__main__":
    p = Prompts.get_prompt(PromptTypes.SALES_AGENT_CONVERSATION_PROMPT)
    print(p)
