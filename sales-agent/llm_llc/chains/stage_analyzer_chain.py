from langchain import LLMChain, PromptTemplate
from langchain.llms import BaseLLM

from llm_llc.loggers.time_logger import time_logger
from llm_llc.prompts.prompts import PromptTypes, Prompts


class StageAnalyzerChain(LLMChain):
    """Chain to analyze which conversation stage should the conversation move into."""

    @classmethod
    @time_logger
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        stage_analyzer_inception_prompt_template = Prompts.get_prompt(
            PromptTypes.STAGE_ANALYZER_PROMPT
        )

        prompt = PromptTemplate(
            template=stage_analyzer_inception_prompt_template,
            input_variables=[
                "conversation_history",
                "conversation_stage_id",
                "conversation_stages",
            ],
        )
        return cls(prompt=prompt, llm=llm, verbose=verbose)
