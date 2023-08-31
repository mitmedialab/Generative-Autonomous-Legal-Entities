from copy import deepcopy
from typing import Any, Dict, List, Union

from langchain import LLMChain
from langchain.agents import AgentExecutor, LLMSingleActionAgent
from langchain.chains import RetrievalQA
from langchain.chains.base import Chain
from langchain.llms import BaseLLM
from pydantic import BaseModel, Field
from llm_llc.chains.sales_conv_chain import SalesConversationChain
from llm_llc.chains.stage_analyzer_chain import StageAnalyzerChain

from llm_llc.loggers.time_logger import time_logger
from llm_llc.parsers import SalesConvoOutputParser
from llm_llc.prompts.prompts import PromptTypes, Prompts
from llm_llc.stages import ConversationStages
from llm_llc.templates import CustomPromptTemplateForTools
from llm_llc.tools.product_catalog_tool import get_tools, load_product_catalog


class LlmLlcAgent(Chain, BaseModel):
    conversation_history: List[str] = []
    conversation_stage_id: str = "1"
    current_conversation_stage: str = ConversationStages.get_init()
    conversation_stages: str = ConversationStages.to_str()
    stage_analyzer_chain: StageAnalyzerChain = Field(...)
    sales_agent_executor: Union[AgentExecutor, None] = Field(...)
    knowledge_base: Union[RetrievalQA, None] = Field(...)
    sales_conversation_utterance_chain: SalesConversationChain = Field(...)
    conversation_stage_dict: Dict = ConversationStages.get_dict()

    use_tools: bool = False
    salesperson_name: str
    salesperson_role: str
    company_name: str
    company_business: str
    company_values: str
    conversation_purpose: str
    conversation_type: str

    def retrieve_conversation_stage(self, key):
        return self.conversation_stage_dict.get(key, "1")

    @property
    def input_keys(self) -> List[str]:
        return []

    @property
    def output_keys(self) -> List[str]:
        return []

    @time_logger
    def seed_agent(self):
        # Step 1: seed the conversation
        self.current_conversation_stage = self.retrieve_conversation_stage("1")
        self.conversation_history = []

    @time_logger
    def determine_conversation_stage(self):
        self.conversation_stage_id = self.stage_analyzer_chain.run(
            conversation_history="\n".join(self.conversation_history).rstrip("\n"),
            conversation_stage_id=self.conversation_stage_id,
            conversation_stages=ConversationStages.to_str(),
        )

        print(f">>>Conversation Stage ID: {self.conversation_stage_id}")
        self.current_conversation_stage = self.retrieve_conversation_stage(
            self.conversation_stage_id
        )

        print(f">>>Conversation Stage: {self.current_conversation_stage}")

    def human_step(self, human_input):
        # process human input
        human_input = "User: " + human_input + " <END_OF_TURN>"
        self.conversation_history.append(human_input)

    @time_logger
    def step(
        self, return_streaming_generator: bool = False, model_name="gpt-3.5-turbo-0613"
    ):
        """
        Args:
            return_streaming_generator (bool): whether or not return
            streaming generator object to manipulate streaming chunks in downstream applications.
        """
        if not return_streaming_generator:
            self._call(inputs={})
        else:
            return self._streaming_generator(model_name=model_name)

    # TO-DO change this override "run" override the "run method" in the SalesConversation chain!
    @time_logger
    def _streaming_generator(self, model_name="gpt-3.5-turbo-0613"):
        prompt = self.sales_conversation_utterance_chain.prep_prompts(
            [
                dict(
                    conversation_stages=self.conversation_stages,
                    conversation_stage=self.current_conversation_stage,
                    conversation_history="\n".join(self.conversation_history),
                    salesperson_name=self.salesperson_name,
                    salesperson_role=self.salesperson_role,
                    company_name=self.company_name,
                    company_business=self.company_business,
                    company_values=self.company_values,
                    conversation_purpose=self.conversation_purpose,
                    conversation_type=self.conversation_type,
                )
            ]
        )

        inception_messages = prompt[0][0].to_messages()

        message_dict = {"role": "system", "content": inception_messages[0].content}

        if self.sales_conversation_utterance_chain.verbose:
            print("\033[92m" + inception_messages[0].content + "\033[0m")
        messages = [message_dict]

        return self.sales_conversation_utterance_chain.llm.completion_with_retry(
            messages=messages,
            stop="<END_OF_TURN>",
            stream=True,
            model=model_name,
        )

    def _call(self, inputs: Dict[str, Any]) -> None:
        if self.use_tools:
            ai_message = self.sales_agent_executor.run(
                input="",
                conversation_stages=self.conversation_stages,
                conversation_stage=self.current_conversation_stage,
                conversation_history="\n".join(self.conversation_history),
                salesperson_name=self.salesperson_name,
                salesperson_role=self.salesperson_role,
                company_name=self.company_name,
                company_business=self.company_business,
                company_values=self.company_values,
                conversation_purpose=self.conversation_purpose,
                conversation_type=self.conversation_type,
            )

        else:
            # else
            ai_message = self.sales_conversation_utterance_chain.run(
                conversation_stages=self.conversation_stages,
                conversation_stage=self.current_conversation_stage,
                conversation_history="\n".join(self.conversation_history),
                salesperson_name=self.salesperson_name,
                salesperson_role=self.salesperson_role,
                company_name=self.company_name,
                company_business=self.company_business,
                company_values=self.company_values,
                conversation_purpose=self.conversation_purpose,
                conversation_type=self.conversation_type,
            )

        if "<END_OF_TURN>" not in ai_message:
            ai_message += " <END_OF_TURN>"
        self.conversation_history.append(ai_message)
        print(ai_message.replace("<END_OF_TURN>", ""))
        return {}

    @classmethod
    @time_logger
    def from_llm(cls, llm: BaseLLM, verbose: bool = False, **kwargs) -> "LlmLlcAgent":
        """Initialize the SalesGPT Controller."""
        stage_analyzer_chain = StageAnalyzerChain.from_llm(llm, verbose=verbose)
        print(kwargs)
        if (
            "use_custom_prompt" in kwargs.keys()
            and kwargs["use_custom_prompt"] == "True"
        ):
            use_custom_prompt = deepcopy(kwargs["use_custom_prompt"])
            custom_prompt = deepcopy(kwargs["custom_prompt"])

            # clean up
            del kwargs["use_custom_prompt"]
            del kwargs["custom_prompt"]

            sales_conversation_utterance_chain = SalesConversationChain.from_llm(
                llm,
                verbose=verbose,
                use_custom_prompt=use_custom_prompt,
                custom_prompt=custom_prompt,
            )

        else:
            sales_conversation_utterance_chain = SalesConversationChain.from_llm(
                llm, verbose=verbose
            )

        if "use_tools" in kwargs.keys() and kwargs["use_tools"] is True:
            # set up agent with tools
            product_catalog = kwargs["product_catalog"]
            knowledge_base = load_product_catalog(product_catalog)
            tools = get_tools(knowledge_base)

            template = Prompts.get_prompt(PromptTypes.SALES_AGENT_TOOLS_PROMPT)

            prompt = CustomPromptTemplateForTools(
                # template=Prompts.get_prompt(PromptTypes.SALES_AGENT_TOOLS_PROMPT),
                template=template,
                tools_getter=lambda x: tools,
                # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
                # This includes the `intermediate_steps` variable because that is needed
                input_variables=[
                    "input",
                    "conversation_stages",
                    "intermediate_steps",
                    "salesperson_name",
                    "salesperson_role",
                    "company_name",
                    "company_business",
                    "company_values",
                    "conversation_purpose",
                    "conversation_type",
                    "conversation_history",
                ],
            )
            llm_chain = LLMChain(llm=llm, prompt=prompt, verbose=verbose)

            tool_names = [tool.name for tool in tools]

            output_parser = SalesConvoOutputParser(ai_prefix=kwargs["salesperson_name"])

            sales_agent_with_tools = LLMSingleActionAgent(
                llm_chain=llm_chain,
                output_parser=output_parser,
                stop=["\nObservation:"],
                allowed_tools=tool_names,
            )

            sales_agent_executor = AgentExecutor.from_agent_and_tools(
                agent=sales_agent_with_tools, tools=tools, verbose=verbose
            )
        else:
            sales_agent_executor = None
            knowledge_base = None

        return cls(
            stage_analyzer_chain=stage_analyzer_chain,
            sales_conversation_utterance_chain=sales_conversation_utterance_chain,
            sales_agent_executor=sales_agent_executor,
            knowledge_base=knowledge_base,
            verbose=verbose,
            **kwargs,
        )
