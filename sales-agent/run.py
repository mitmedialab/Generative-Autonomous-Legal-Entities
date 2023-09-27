import argparse

import os
import json
import time

from llm_llc.agents.sales_agents import LlmLlcAgent
from langchain.chat_models import ChatOpenAI

from llm_llc.gmail.gmail import (
    get_history,
    mark_email_as_read,
    process_unread_emails,
    reply,
)
from llm_llc.loggers.audit_logger import AuditLogger


if __name__ == "__main__":
    # import your OpenAI key (put in your .env file)
    with open(".env", "r") as f:
        env_file = f.readlines()
    envs_dict = {
        key.strip("'"): value.strip("\n")
        for key, value in [(i.split("=")) for i in env_file]
    }
    os.environ["OPENAI_API_KEY"] = envs_dict["OPENAI_API_KEY"]

    # Access arguments
    config_path = "kb/agent_config.json"
    verbose = True
    max_num_turns = 10

    audit = AuditLogger()

    llm = ChatOpenAI(temperature=0.1)

    with open(config_path, "r") as f:
        config = json.load(f)
    audit.info(f"Agent config {config}")
    sales_agent = LlmLlcAgent.from_llm(llm, verbose=verbose, **config)

    sales_agent.seed_agent()
    print("=" * 10)
    cnt = 0
    while True:
        emails = process_unread_emails()
        if emails:
            for email in emails:
                if email:
                    print(email)
                    threadId = email["msg"]["threadId"]
                    # retieve the conversation history from the email thread
                    conv_history = get_history(threadId)

                    # remove the most recent item from history
                    last_email = conv_history.pop(-1)
                    sales_agent.conversation_history = conv_history

                    # log the most recent email, conv history and conv stage
                    stage = sales_agent.get_conversation_stage()
                    audit.log_incoming_message(
                        "test", last_email, conv_history, conversation_stage=stage
                    )

                    sales_agent.human_step(last_email)
                    sales_agent.step()

                    agent_reply = sales_agent.conversation_history[-1]
                    agent_reply = "".join(agent_reply.split("<END_OF_TURN>"))
                    # end conversation
                    if "<END_OF_CALL>" in agent_reply:
                        audit.info(
                            "Sales Agent determined it is time to end the thread."
                        )
                        break
                    reply(
                        reply_message=agent_reply,
                        original_email_id=email["msg"]["id"],
                        threadId=threadId,
                    )
                    stage = sales_agent.get_conversation_stage()
                    audit.log_reply(reply=agent_reply, conversation_stage=stage)
                    mark_email_as_read(email["msg"]["id"])

        time.sleep(30)
