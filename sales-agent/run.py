import argparse

import os
import json
import time

from llm_llc.agents.sales_agents import LlmLlcAgent
from langchain.chat_models import ChatOpenAI

from llm_llc.gmail.gmail import mark_email_as_read, process_unread_emails, reply


if __name__ == "__main__":
    # import your OpenAI key (put in your .env file)
    with open(".env", "r") as f:
        env_file = f.readlines()
    envs_dict = {
        key.strip("'"): value.strip("\n")
        for key, value in [(i.split("=")) for i in env_file]
    }
    os.environ["OPENAI_API_KEY"] = envs_dict["OPENAI_API_KEY"]

    # Initialize argparse
    parser = argparse.ArgumentParser(description="Description of your program")

    # Add arguments
    parser.add_argument(
        "--config", type=str, help="Path to agent config file", default=""
    )
    parser.add_argument("--verbose", type=bool, help="Verbosity", default=False)
    parser.add_argument(
        "--max_num_turns",
        type=int,
        help="Maximum number of turns in the sales conversation",
        default=10,
    )

    # Parse arguments
    args = parser.parse_args()

    # Access arguments
    config_path = "kb/agent_config.json"
    verbose = args.verbose
    max_num_turns = args.max_num_turns

    llm = ChatOpenAI(temperature=0.2)

    with open(config_path, "r") as f:
        config = json.load(f)
    print(f"Agent config {config}")
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
                    sales_agent.human_step(email["body"][0].contents[0])
                    sales_agent.step()
                    agent_reply = sales_agent.conversation_history[-1]
                    agent_reply = "".join(agent_reply.split("<END_OF_TURN>"))
                    # end conversation
                    if "<END_OF_CALL>" in agent_reply:
                        print("Sales Agent determined it is time to end the thread.")
                        break
                    reply(
                        reply_message=agent_reply,
                        original_email_id=email["msg"]["id"],
                    )
                    mark_email_as_read(email["msg"]["id"])

        time.sleep(30)
