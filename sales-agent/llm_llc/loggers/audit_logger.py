import logging


class AuditLogger(logging.Logger):
    def __init__(self, level=logging.NOTSET):
        super().__init__("audit", level)
        audit_file_handler = logging.FileHandler("llmllc-sales-audit.log")
        audit_file_handler.setLevel(logging.INFO)
        app_formatter = logging.Formatter("%(asctime)s - %(message)s")
        audit_file_handler.setFormatter(app_formatter)
        self.addHandler(audit_file_handler)

    def log_incoming_message(
        self, sender, message, conversation_history, conversation_stage
    ):
        # Add custom logging methods or functionality here
        conversation_history_str = "".join(
            [f">>> {''.join(item.splitlines())}\n" for item in conversation_history]
        )
        self.info(
            f"""Incoming message from: {sender} 
Body: {message} 
Conversation stage: {conversation_stage} 
Conversation history: 
{conversation_history_str}
"""
        )

    def log_reply(self, reply, conversation_stage):
        self.info(
            f"""Reply: {reply}
                  Stage: {conversation_stage}"""
        )
